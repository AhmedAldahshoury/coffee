from datetime import datetime, timezone
import logging
from uuid import UUID

import optuna
from optuna.importance import get_param_importances
from sqlalchemy import select
from sqlalchemy.orm import Session

from coffee_backend.core.config import get_settings
from coffee_backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from coffee_backend.db.models.brew import Brew
from coffee_backend.db.models.optuna_study import Suggestion
from coffee_backend.schemas.optimisation import OptimisationInsight, StudyRequest
from coffee_backend.schemas.parameter_registry import METHOD_PARAMETER_REGISTRY


class OptimisationService:
    MIN_SCORE = 0.0
    MAX_SCORE = 10.0

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.storage = optuna.storages.RDBStorage(
            url=self.settings.database_url,
            skip_compatibility_check=self.settings.optuna_skip_compatibility_check,
        )
        self.logger = logging.getLogger(__name__)

    def _normalise_method(self, method: str) -> str:
        normalised_method = method.strip().lower()
        if normalised_method not in METHOD_PARAMETER_REGISTRY:
            raise ValidationError("Unsupported method", code="unsupported_method")
        return normalised_method

    def build_study_key(self, user_id: UUID, req: StudyRequest) -> str:
        method = self._normalise_method(req.method)
        return (
            f"u:{user_id}:m:{method}:b:{req.bean_id or 'none'}:"
            f"e:{req.equipment_id or 'none'}:r:{req.recipe_id or 'none'}"
        )

    def ensure_study(self, user_id: UUID, req: StudyRequest) -> str:
        study_key = self.build_study_key(user_id, req)
        sampler = optuna.samplers.TPESampler(seed=42, n_startup_trials=5)
        optuna.create_study(
            study_name=study_key,
            storage=self.storage,
            direction="maximize",
            load_if_exists=True,
            sampler=sampler,
        )
        self.logger.info("optimisation.study.ensured", extra={"study_key": study_key})
        return study_key

    def _ask_params(self, trial: optuna.Trial, method: str) -> dict[str, object]:
        schema = METHOD_PARAMETER_REGISTRY.get(method)
        if schema is None:
            raise ValidationError("Unsupported method")
        params: dict[str, object] = {}
        for name, spec in schema.items():
            if spec["type"] == "int":
                params[name] = trial.suggest_int(name, spec["min"], spec["max"])
            elif spec["type"] == "float":
                params[name] = trial.suggest_float(name, spec["min"], spec["max"])
            elif spec["type"] == "categorical":
                params[name] = trial.suggest_categorical(name, spec["choices"])
        return params

    def suggest(self, user_id: UUID, req: StudyRequest) -> Suggestion:
        req = req.model_copy(update={"method": self._normalise_method(req.method)})
        study_key = self.ensure_study(user_id, req)
        study = optuna.load_study(study_name=study_key, storage=self.storage)
        trial = study.ask()
        params = self._ask_params(trial, req.method)
        suggestion = Suggestion(
            user_id=user_id,
            study_key=study_key,
            trial_number=trial.number,
            suggested_parameters=params,
            status="issued",
        )
        self.db.add(suggestion)
        self.db.commit()
        self.db.refresh(suggestion)
        self.logger.info(
            "optimisation.suggestion.issued",
            extra={
                "study_key": study_key,
                "trial_number": trial.number,
                "suggestion_id": str(suggestion.id),
            },
        )
        return suggestion

    def _validate_score(self, score: float | None) -> float:
        if score is None:
            raise ValidationError(
                "Score is required when applying suggestion",
                code="suggestion_score_required",
            )
        if not (self.MIN_SCORE <= float(score) <= self.MAX_SCORE):
            raise ValidationError(
                f"Score must be between {self.MIN_SCORE} and {self.MAX_SCORE}",
                code="suggestion_score_out_of_range",
            )
        return float(score)

    def apply(
        self, user_id: UUID, suggestion_id: UUID, brew_id: UUID, score: float | None, failed: bool
    ) -> Suggestion:
        suggestion = self.db.scalar(
            select(Suggestion).where(Suggestion.id == suggestion_id, Suggestion.user_id == user_id)
        )
        if suggestion is None:
            raise NotFoundError("Suggestion not found", code="suggestion_not_found")
        if suggestion.status == "applied":
            raise ConflictError(
                "Suggestion was already applied and cannot be applied again",
                code="suggestion_already_applied",
            )
        brew = self.db.scalar(select(Brew).where(Brew.id == brew_id, Brew.user_id == user_id))
        if brew is None:
            raise NotFoundError("Brew not found", code="brew_not_found")
        try:
            study = optuna.load_study(study_name=suggestion.study_key, storage=self.storage)
        except KeyError as exc:
            raise NotFoundError("Study not found", code="study_not_found") from exc

        try:
            study.get_trial(suggestion.trial_number)
        except KeyError as exc:
            raise NotFoundError("Suggestion trial not found", code="suggestion_trial_not_found") from exc

        candidate_value = (
            self.settings.failed_brew_score
            if failed
            else (score if score is not None else brew.score)
        )
        value = self._validate_score(candidate_value)
        study.tell(suggestion.trial_number, value)
        suggestion.brew_id = brew_id
        suggestion.status = "applied"
        brew.score = value
        brew.failed = failed
        self.db.commit()
        self.db.refresh(suggestion)
        self.logger.info(
            "optimisation.suggestion.applied",
            extra={
                "study_key": suggestion.study_key,
                "trial_number": suggestion.trial_number,
                "suggestion_id": str(suggestion.id),
                "brew_id": str(brew_id),
                "score": value,
                "failed": failed,
            },
        )
        return suggestion

    def insights(self, study_key: str) -> OptimisationInsight:
        study = optuna.load_study(study_name=study_key, storage=self.storage)
        completed = [t for t in study.get_trials(deepcopy=False) if t.value is not None]
        importance = get_param_importances(study) if len(completed) >= 3 else {}
        return OptimisationInsight(
            study_key=study_key,
            trial_count=len(completed),
            parameter_importance=importance,
            generated_at=datetime.now(timezone.utc),
        )
