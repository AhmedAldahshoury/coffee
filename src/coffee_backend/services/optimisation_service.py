import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import optuna
from optuna.importance import get_param_importances
from sqlalchemy import select
from sqlalchemy.orm import Session

from coffee_backend.core.config import get_settings
from coffee_backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from coffee_backend.db.models.brew import Brew
from coffee_backend.db.models.method_profile import MethodProfile
from coffee_backend.db.models.optuna_study import StudyContext, Suggestion
from coffee_backend.schemas.optimisation import OptimisationInsight, StudyRequest


@dataclass(frozen=True)
class CanonicalStudyContext:
    user_id: UUID
    method_id: str
    variant_id: str
    bean_id: UUID | None
    equipment_id: UUID | None


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

    def _resolve_variant_id(self, method_id: str, variant_id: str | None) -> str:
        method = method_id.strip().lower()
        if variant_id is not None:
            profile = self.db.scalar(
                select(MethodProfile)
                .where(MethodProfile.method_id == method)
                .where(MethodProfile.variant_id == variant_id)
                .order_by(MethodProfile.schema_version.desc())
            )
            if profile is None:
                raise ValidationError(
                    f"Unsupported method variant '{method}/{variant_id}'",
                    code="unsupported_method_variant",
                )
            return variant_id

        profiles = list(
            self.db.scalars(
                select(MethodProfile)
                .where(MethodProfile.method_id == method)
                .order_by(MethodProfile.variant_id.asc(), MethodProfile.schema_version.desc())
            )
        )
        if not profiles:
            raise ValidationError("Unsupported method", code="unsupported_method")
        default_variant = next((p.variant_id for p in profiles if "default" in p.variant_id), None)
        return default_variant or profiles[0].variant_id

    def canonicalise_context(self, user_id: UUID, req: StudyRequest) -> CanonicalStudyContext:
        method_id = req.method_id.strip().lower()
        variant_id = self._resolve_variant_id(method_id, req.variant_id)
        return CanonicalStudyContext(
            user_id=user_id,
            method_id=method_id,
            variant_id=variant_id,
            bean_id=req.bean_id,
            equipment_id=req.equipment_id,
        )

    def build_study_key(self, context: CanonicalStudyContext) -> str:
        return (
            f"u:{context.user_id}|m:{context.method_id}|v:{context.variant_id}|"
            f"b:{context.bean_id or 'none'}|e:{context.equipment_id or 'none'}"
        )

    def ensure_study_context(self, user_id: UUID, req: StudyRequest) -> StudyContext:
        context = self.canonicalise_context(user_id, req)
        study_key = self.build_study_key(context)
        study_context = self.db.scalar(
            select(StudyContext).where(StudyContext.study_key == study_key)
        )
        if study_context is None:
            study_context = StudyContext(
                user_id=context.user_id,
                method_id=context.method_id,
                variant_id=context.variant_id,
                bean_id=context.bean_id,
                equipment_id=context.equipment_id,
                study_key=study_key,
            )
            self.db.add(study_context)
            self.db.commit()
            self.db.refresh(study_context)

        sampler = optuna.samplers.TPESampler(seed=42, n_startup_trials=5)
        optuna.create_study(
            study_name=study_key,
            storage=self.storage,
            direction="maximize",
            load_if_exists=True,
            sampler=sampler,
        )
        self.logger.info("optimisation.study.ensured", extra={"study_key": study_key})
        return study_context

    def _ask_params(
        self, trial: optuna.Trial, method_id: str, variant_id: str
    ) -> dict[str, object]:
        profile = self.db.scalar(
            select(MethodProfile)
            .where(MethodProfile.method_id == method_id)
            .where(MethodProfile.variant_id == variant_id)
            .order_by(MethodProfile.schema_version.desc())
        )
        if profile is None:
            raise ValidationError("Unsupported method", code="unsupported_method")
        params: dict[str, object] = {}
        for spec in profile.parameters:
            name = str(spec["name"])
            if spec["type"] == "int":
                params[name] = trial.suggest_int(name, spec["min"], spec["max"])
            elif spec["type"] == "float":
                params[name] = trial.suggest_float(name, spec["min"], spec["max"])
            elif spec["type"] == "categorical":
                params[name] = trial.suggest_categorical(name, spec["choices"])
        return params

    def suggest(self, user_id: UUID, req: StudyRequest) -> Suggestion:
        study_context = self.ensure_study_context(user_id, req)
        study_key = study_context.study_key
        study = optuna.load_study(study_name=study_key, storage=self.storage)
        trial = study.ask()
        params = self._ask_params(trial, study_context.method_id, study_context.variant_id)
        suggestion = Suggestion(
            user_id=user_id,
            study_context_id=study_context.id,
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

        if (
            brew.method != suggestion.study_context.method_id
            or brew.variant_id != suggestion.study_context.variant_id
            or brew.bean_id != suggestion.study_context.bean_id
            or brew.equipment_id != suggestion.study_context.equipment_id
        ):
            raise ValidationError(
                "Suggestion context does not match brew context",
                code="suggestion_context_mismatch",
            )

        try:
            study = optuna.load_study(study_name=suggestion.study_key, storage=self.storage)
        except KeyError as exc:
            raise NotFoundError("Study not found", code="study_not_found") from exc

        known_trial_numbers = {trial.number for trial in study.get_trials(deepcopy=False)}
        if suggestion.trial_number not in known_trial_numbers:
            raise NotFoundError(
                "Suggestion trial not found",
                code="suggestion_trial_not_found",
            )

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
