import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isclose
from uuid import UUID

import optuna
from optuna.importance import get_param_importances
from optuna.trial import create_trial
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from coffee_backend.core.config import get_settings
from coffee_backend.core.exceptions import ConflictError, NotFoundError, ValidationError
from coffee_backend.db.models.brew import Brew
from coffee_backend.db.models.enums import BrewStatus
from coffee_backend.db.models.method_profile import MethodProfile
from coffee_backend.db.models.optuna_study import StudyContext, Suggestion
from coffee_backend.schemas.optimisation import (
    OptimisationInsight,
    StudyRequest,
    WarmStartRequest,
    WarmStartResponse,
)


@dataclass(frozen=True)
class WarmStartCandidate:
    dedupe_key: str
    brew_id: UUID
    parameters: dict[str, object]
    score: float


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

    def _get_method_profile(self, method_id: str, variant_id: str) -> MethodProfile:
        profile = self.db.scalar(
            select(MethodProfile)
            .where(MethodProfile.method_id == method_id)
            .where(MethodProfile.variant_id == variant_id)
            .order_by(MethodProfile.schema_version.desc())
        )
        if profile is None:
            raise ValidationError(
                f"Unsupported method variant '{method_id}/{variant_id}'",
                code="unsupported_method_variant",
            )
        return profile

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

    def _suggest_param_from_spec(self, trial: optuna.Trial, spec: dict[str, object]) -> object:
        name = str(spec["name"])
        ptype = str(spec["type"])
        if ptype == "int":
            step = int(spec.get("step") or 1)
            return trial.suggest_int(name, int(spec["min"]), int(spec["max"]), step=step)
        if ptype == "float":
            step = spec.get("step")
            if step is not None:
                return trial.suggest_float(
                    name,
                    float(spec["min"]),
                    float(spec["max"]),
                    step=float(step),
                )
            return trial.suggest_float(name, float(spec["min"]), float(spec["max"]))
        if ptype == "bool":
            return trial.suggest_categorical(name, [True, False])
        if ptype in {"enum", "categorical"}:
            choices = spec.get("choices")
            if not isinstance(choices, list) or not choices:
                raise ValidationError(
                    f"Parameter '{name}' enum/categorical requires non-empty choices",
                    code="invalid_method_profile",
                )
            return trial.suggest_categorical(name, choices)
        raise ValidationError(
            f"Unsupported parameter type '{ptype}' for '{name}'",
            code="invalid_method_profile",
        )

    def _validate_param_against_spec(self, spec: dict[str, object], value: object) -> None:
        name = str(spec["name"])
        ptype = str(spec["type"])

        if ptype == "int":
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValidationError(
                    f"Invalid value for '{name}': expected int",
                    code="invalid_suggested_params",
                    fields={name: "expected int"},
                )
            min_v = int(spec["min"])
            max_v = int(spec["max"])
            step = int(spec.get("step") or 1)
            if value < min_v or value > max_v or ((value - min_v) % step != 0):
                raise ValidationError(
                    (
                        f"Invalid value for '{name}': {value} must be between {min_v} and {max_v} "
                        f"with step {step}"
                    ),
                    code="invalid_suggested_params",
                    fields={name: f"between {min_v}-{max_v} step {step}"},
                )
            return

        if ptype == "float":
            if not isinstance(value, (float, int)) or isinstance(value, bool):
                raise ValidationError(
                    f"Invalid value for '{name}': expected number",
                    code="invalid_suggested_params",
                    fields={name: "expected number"},
                )
            f_value = float(value)
            min_v = float(spec["min"])
            max_v = float(spec["max"])
            if f_value < min_v or f_value > max_v:
                raise ValidationError(
                    f"Invalid value for '{name}': {f_value} must be between {min_v} and {max_v}",
                    code="invalid_suggested_params",
                    fields={name: f"between {min_v}-{max_v}"},
                )
            step = spec.get("step")
            if step is not None:
                step_v = float(step)
                remainder = (f_value - min_v) / step_v
                if not isclose(remainder, round(remainder), abs_tol=1e-9):
                    raise ValidationError(
                        (
                            f"Invalid value for '{name}': {f_value} must follow step {step_v} "
                            f"from {min_v}"
                        ),
                        code="invalid_suggested_params",
                        fields={name: f"step {step_v} from {min_v}"},
                    )
            return

        if ptype == "bool":
            if not isinstance(value, bool):
                raise ValidationError(
                    f"Invalid value for '{name}': expected bool",
                    code="invalid_suggested_params",
                    fields={name: "expected bool"},
                )
            return

        if ptype in {"enum", "categorical"}:
            choices = spec.get("choices")
            if value not in choices:
                raise ValidationError(
                    f"Invalid value for '{name}': choose one of {choices}",
                    code="invalid_suggested_params",
                    fields={name: f"one of {choices}"},
                )
            return

        raise ValidationError(
            f"Unsupported parameter type '{ptype}' for '{name}'",
            code="invalid_method_profile",
        )

    def _validate_hard_caps(self, method_id: str, params: dict[str, object]) -> None:
        if method_id == "v60" and "total_time_s" in params:
            value = params["total_time_s"]
            if not isinstance(value, int):
                raise ValidationError(
                    "Invalid value for 'total_time_s': expected int",
                    code="invalid_suggested_params",
                    fields={"total_time_s": "expected int"},
                )
            if not (120 <= value <= 300):
                raise ValidationError(
                    "Invalid value for 'total_time_s': must be within hard cap 120-300 seconds",
                    code="invalid_suggested_params",
                    fields={"total_time_s": "hard cap 120-300"},
                )

        if method_id == "aeropress" and "plunge_s" in params:
            value = params["plunge_s"]
            if not isinstance(value, int):
                raise ValidationError(
                    "Invalid value for 'plunge_s': expected int",
                    code="invalid_suggested_params",
                    fields={"plunge_s": "expected int"},
                )
            if value > 60:
                raise ValidationError(
                    "Invalid value for 'plunge_s': must be <= 60 seconds hard cap",
                    code="invalid_suggested_params",
                    fields={"plunge_s": "hard cap <= 60"},
                )

    def _distributions_for_profile(
        self, profile: MethodProfile
    ) -> dict[str, optuna.distributions.BaseDistribution]:
        distributions: dict[str, optuna.distributions.BaseDistribution] = {}
        for spec in profile.parameters:
            name = str(spec["name"])
            ptype = str(spec["type"])
            if ptype == "int":
                distributions[name] = optuna.distributions.IntDistribution(
                    low=int(spec["min"]), high=int(spec["max"]), step=int(spec.get("step") or 1)
                )
            elif ptype == "float":
                step = spec.get("step")
                distributions[name] = optuna.distributions.FloatDistribution(
                    low=float(spec["min"]),
                    high=float(spec["max"]),
                    step=float(step) if step is not None else None,
                )
            elif ptype == "bool":
                distributions[name] = optuna.distributions.CategoricalDistribution(
                    choices=[True, False]
                )
            elif ptype in {"enum", "categorical"}:
                choices = spec.get("choices")
                if not isinstance(choices, list) or not choices:
                    raise ValidationError(
                        f"Parameter '{name}' enum/categorical requires non-empty choices",
                        code="invalid_method_profile",
                    )
                distributions[name] = optuna.distributions.CategoricalDistribution(choices=choices)
            else:
                raise ValidationError(
                    f"Unsupported parameter type '{ptype}' for '{name}'",
                    code="invalid_method_profile",
                )
        return distributions

    def _validate_params_for_profile(
        self,
        method_id: str,
        params: dict[str, object],
        profile: MethodProfile,
    ) -> None:
        definitions = {str(spec["name"]): spec for spec in profile.parameters}
        unknown = sorted(key for key in params if key not in definitions)
        if unknown:
            raise ValidationError(
                "Suggested params contain unknown parameter keys for this method profile",
                code="invalid_suggested_params",
                fields=dict.fromkeys(unknown, "unknown parameter for profile"),
            )

        for key, spec in definitions.items():
            if key not in params:
                raise ValidationError(
                    f"Suggested params missing '{key}'",
                    code="invalid_suggested_params",
                    fields={key: "missing parameter"},
                )
            self._validate_param_against_spec(spec, params[key])

        self._validate_hard_caps(method_id, params)

    def _normalise_param_value(self, value: object) -> object:
        if isinstance(value, dict):
            return {str(k): self._normalise_param_value(v) for k, v in sorted(value.items())}
        if isinstance(value, list):
            return [self._normalise_param_value(v) for v in value]
        return value

    def _dedupe_key_for_brew(self, study_key: str, brew: Brew) -> str:
        if brew.id is not None:
            return f"brew:{brew.id}"
        payload = {
            "study_key": study_key,
            "params": self._normalise_param_value(dict(brew.parameters)),
            "brewed_at": brew.brewed_at.isoformat() if brew.brewed_at is not None else None,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return f"hash:{hashlib.sha256(encoded).hexdigest()}"

    def _study_existing_warm_start_keys(self, study: optuna.Study) -> set[str]:
        keys: set[str] = set()
        for trial in study.get_trials(deepcopy=False):
            attrs = trial.user_attrs or {}
            key = attrs.get("warm_start_key")
            if isinstance(key, str):
                keys.add(key)
        return keys

    def warm_start(self, user_id: UUID, req: WarmStartRequest) -> WarmStartResponse:
        study_context = self.ensure_study_context(user_id, req)
        study_key = study_context.study_key
        profile = self._get_method_profile(study_context.method_id, study_context.variant_id)

        query = (
            select(Brew)
            .where(Brew.user_id == user_id)
            .where(Brew.method == study_context.method_id)
            .where(Brew.variant_id == study_context.variant_id)
            .where(Brew.bean_id == study_context.bean_id)
            .where(Brew.equipment_id == study_context.equipment_id)
            .where(Brew.status == BrewStatus.OK)
            .where(Brew.score.is_not(None))
            .order_by(desc(Brew.brewed_at))
        )
        if req.limit is not None:
            query = query.limit(req.limit)

        brews = list(self.db.scalars(query))
        candidates: list[WarmStartCandidate] = []
        for brew in brews:
            params = dict(brew.parameters)
            self._validate_params_for_profile(study_context.method_id, params, profile)
            candidates.append(
                WarmStartCandidate(
                    dedupe_key=self._dedupe_key_for_brew(study_key, brew),
                    brew_id=brew.id,
                    parameters=params,
                    score=float(brew.score),
                )
            )

        study = optuna.load_study(study_name=study_key, storage=self.storage)
        known_keys = self._study_existing_warm_start_keys(study)
        added = 0

        for candidate in candidates:
            if candidate.dedupe_key in known_keys:
                continue
            trial = create_trial(
                params=candidate.parameters,
                distributions=self._distributions_for_profile(profile),
                value=candidate.score,
                user_attrs={
                    "warm_start": True,
                    "warm_start_key": candidate.dedupe_key,
                    "warm_start_brew_id": str(candidate.brew_id),
                },
            )
            study.add_trial(trial)
            known_keys.add(candidate.dedupe_key)
            added += 1

        skipped = len(candidates) - added
        self.logger.info(
            "optimisation.warm_start.completed",
            extra={
                "study_key": study_key,
                "scanned": len(candidates),
                "added": added,
                "skipped": skipped,
            },
        )

        return WarmStartResponse(
            study_key=study_key,
            scanned=len(candidates),
            added=added,
            skipped=skipped,
        )

    def suggest(self, user_id: UUID, req: StudyRequest) -> Suggestion:
        study_context = self.ensure_study_context(user_id, req)
        study_key = study_context.study_key
        profile = self._get_method_profile(study_context.method_id, study_context.variant_id)

        study = optuna.load_study(study_name=study_key, storage=self.storage)
        trial = study.ask()
        params = {
            str(spec["name"]): self._suggest_param_from_spec(trial, spec)
            for spec in profile.parameters
        }
        self._validate_params_for_profile(study_context.method_id, params, profile)

        suggestion = Suggestion(
            user_id=user_id,
            study_context_id=study_context.id,
            study_key=study_key,
            trial_number=trial.number,
            suggested_params=params,
            actual_params=None,
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
                "Score is required when applying a non-failed brew suggestion",
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

        brew_method = brew.method.value if hasattr(brew.method, "value") else str(brew.method)
        if (
            brew_method != suggestion.study_context.method_id
            or brew.variant_id != suggestion.study_context.variant_id
            or brew.bean_id != suggestion.study_context.bean_id
            or brew.equipment_id != suggestion.study_context.equipment_id
        ):
            raise ValidationError(
                "Suggestion context does not match brew context. Ensure method, variant, "
                "bean, and equipment are identical.",
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

        if failed:
            objective = float(self.settings.failed_brew_score)
            brew.status = BrewStatus.FAILED
            brew.score = None
        else:
            candidate_value = score if score is not None else brew.score
            objective = self._validate_score(candidate_value)
            brew.status = BrewStatus.OK
            brew.score = objective

        study.tell(suggestion.trial_number, objective)

        suggestion.brew_id = brew_id
        suggestion.actual_params = dict(brew.parameters)
        suggestion.status = "applied"
        self.db.commit()
        self.db.refresh(suggestion)
        self.logger.info(
            "optimisation.suggestion.applied",
            extra={
                "study_key": suggestion.study_key,
                "trial_number": suggestion.trial_number,
                "suggestion_id": str(suggestion.id),
                "brew_id": str(brew_id),
                "objective": objective,
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
