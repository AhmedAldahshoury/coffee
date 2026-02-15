from __future__ import annotations

from dataclasses import dataclass
from time import gmtime, strftime

import optuna
import pandas as pd
from optuna.distributions import CategoricalDistribution, FloatDistribution, IntDistribution

from app.core.errors import DataValidationError
from app.schemas.optimization import OptimizationRequest, OptimizationResponse, SuggestedParameter

NO_OPTIMIZE_COLUMNS = ["date", "comments"]
OBJECTIVE_COLUMN = "score"
FAILED_COLUMN = "failed"
FAILED_SCORE = -1


@dataclass
class ParsedExperiment:
    historical_df: pd.DataFrame
    fixed_parameters: dict[str, str | int | float]
    unique_category_dict: dict[str, list]


class OptimizerService:
    def __init__(self, seed: int) -> None:
        self.seed = seed

    def optimize(
        self,
        request: OptimizationRequest,
        experiments_df: pd.DataFrame,
        metadata_df: pd.DataFrame,
    ) -> OptimizationResponse:
        experiments_df = experiments_df.copy()
        experiments_df.drop(columns=[c for c in NO_OPTIMIZE_COLUMNS if c in experiments_df], inplace=True)
        experiments_df[FAILED_COLUMN] = experiments_df[FAILED_COLUMN].notna()

        parsed = self._parse_experiments(experiments_df, metadata_df, request.persons, request.method)
        distributions = self._get_distributions(metadata_df, parsed.unique_category_dict)

        sampler = optuna.samplers.TPESampler(
            n_startup_trials=0,
            seed=self.seed,
            prior_weight=request.prior_weight,
        )
        study = optuna.create_study(sampler=sampler, direction="maximize", study_name="Coffee Optimization")
        self._add_historical_trials(study, distributions, parsed.historical_df)

        if not study.trials:
            raise DataValidationError("No historical trials available for optimization.")

        if request.best_only:
            next_parameters = study.best_params
            score = float(study.best_value)
        else:
            objective = self._get_objective(distributions, parsed.fixed_parameters)
            study.optimize(objective, n_trials=1)
            next_parameters = study.trials[-1].params
            score = None

        suggested = [
            self._build_suggested_parameter(name, value, metadata_df, fixed=False)
            for name, value in next_parameters.items()
        ]
        suggested.extend(
            self._build_suggested_parameter(name, value, metadata_df, fixed=True)
            for name, value in parsed.fixed_parameters.items()
        )

        return OptimizationResponse(score=score, suggested_parameters=suggested)

    def _build_suggested_parameter(
        self, parameter: str, value: str | int | float, metadata_df: pd.DataFrame, fixed: bool
    ) -> SuggestedParameter:
        parameter_metadata = metadata_df[metadata_df["name"] == parameter]
        if parameter_metadata.empty:
            return SuggestedParameter(name=parameter, value=value, fixed=fixed)

        unit = parameter_metadata["unit"].values[0]
        if unit == "seconds" and isinstance(value, (int, float)):
            formatted_time = strftime("%M:%S", gmtime(float(value)))
            value = f"{formatted_time} [{value}]"

        return SuggestedParameter(name=parameter, value=value, unit=unit, fixed=fixed)

    def _get_score_columns(self, metadata_df: pd.DataFrame) -> list[str]:
        return metadata_df[metadata_df["type"] == "score"]["name"].tolist()

    def _get_parameter_columns(self, metadata_df: pd.DataFrame) -> list[str]:
        return metadata_df[metadata_df["type"] == "parameter"]["name"].tolist()

    def _filter_score_columns(self, all_score_columns: list[str], persons: list[str] | None) -> list[str]:
        if persons:
            return [col for col in all_score_columns if any(name in col for name in persons)]
        return all_score_columns

    def _parse_experiments(
        self,
        experiments_df: pd.DataFrame,
        metadata_df: pd.DataFrame,
        persons: list[str] | None,
        method: str,
    ) -> ParsedExperiment:
        all_score_columns = self._get_score_columns(metadata_df)
        all_parameter_columns = self._get_parameter_columns(metadata_df)
        person_score_columns = self._filter_score_columns(all_score_columns, persons)
        if not person_score_columns:
            raise DataValidationError("No score columns available for selected person filters.")

        historical_df = experiments_df.dropna(subset=all_parameter_columns)
        fixed_parameters_df = experiments_df.drop(historical_df.index)
        historical_df = historical_df.copy()

        historical_df[OBJECTIVE_COLUMN] = self._get_scores(historical_df, person_score_columns, method)
        historical_df.drop(columns=[c for c in all_score_columns if c in historical_df], inplace=True)

        failed_locations = historical_df[FAILED_COLUMN]
        historical_df.loc[failed_locations, OBJECTIVE_COLUMN] = FAILED_SCORE

        if len(fixed_parameters_df) > 1:
            raise DataValidationError("Multiple partially filled rows found; cannot infer fixed parameters.")

        fixed_parameters: dict[str, str | int | float] = {}
        if not fixed_parameters_df.empty:
            fixed_row = fixed_parameters_df.iloc[0].dropna().drop(labels=[FAILED_COLUMN], errors="ignore")
            fixed_parameters = fixed_row.to_dict()

        return ParsedExperiment(
            historical_df=historical_df,
            fixed_parameters=fixed_parameters,
            unique_category_dict=self._get_unique_categories(historical_df, metadata_df),
        )

    def _get_unique_categories(self, historical_df: pd.DataFrame, metadata_df: pd.DataFrame) -> dict[str, list]:
        category_rows = (metadata_df["type"] == "parameter") & (metadata_df["parameter type"] == "category")
        names = metadata_df[category_rows]["name"].tolist()
        return {name: historical_df[name].dropna().unique().tolist() for name in names}

    def _get_scores(self, historical_df: pd.DataFrame, score_columns: list[str], method: str) -> pd.Series:
        if method == "mean":
            return historical_df[score_columns].mean(axis=1)
        if method == "median":
            return historical_df[score_columns].median(axis=1)
        if method == "lowest":
            return historical_df[score_columns].min(axis=1)
        if method == "highest":
            return historical_df[score_columns].max(axis=1)
        raise DataValidationError(f"Unsupported method: {method}")

    def _get_distributions(
        self, metadata_df: pd.DataFrame, unique_category_dict: dict[str, list]
    ) -> dict[str, CategoricalDistribution | IntDistribution | FloatDistribution]:
        distributions: dict[str, CategoricalDistribution | IntDistribution | FloatDistribution] = {}
        parameter_rows = metadata_df[metadata_df["type"] == "parameter"]
        for _, row in parameter_rows.iterrows():
            name = row["name"]
            type_ = row["parameter type"]
            low = row["low"]
            high = row["high"]
            step = row["step"]

            if type_ == "category":
                distributions[name] = CategoricalDistribution(choices=unique_category_dict.get(name, []))
            elif type_ == "int":
                distributions[name] = IntDistribution(low=int(low), high=int(high), step=int(step))
            elif type_ == "float":
                distributions[name] = FloatDistribution(low=float(low), high=float(high), step=float(step))
        return distributions

    def _sanitize_params(self, params: dict, distributions: dict) -> dict:
        sanitized = params.copy()
        for param_name, param_value in params.items():
            distribution = distributions[param_name]
            if isinstance(distribution, CategoricalDistribution):
                continue
            param_value = min(max(param_value, distribution.low), distribution.high)
            param_value = round((param_value - distribution.low) / distribution.step) * distribution.step + distribution.low
            if isinstance(distribution, IntDistribution):
                param_value = int(param_value)
            sanitized[param_name] = param_value
        return sanitized

    def _get_objective(self, distributions: dict, fixed_parameters: dict):
        def objective(trial: optuna.trial.Trial) -> float:
            for param_name, distribution in distributions.items():
                if param_name in fixed_parameters:
                    continue
                if isinstance(distribution, CategoricalDistribution):
                    trial.suggest_categorical(param_name, distribution.choices)
                elif isinstance(distribution, IntDistribution):
                    trial.suggest_int(param_name, distribution.low, distribution.high, step=distribution.step)
                elif isinstance(distribution, FloatDistribution):
                    trial.suggest_float(param_name, distribution.low, distribution.high, step=distribution.step)
            return 0.0

        return objective

    def _add_historical_trials(self, study: optuna.Study, distributions: dict, historical_df: pd.DataFrame) -> None:
        for _, row in historical_df.iterrows():
            params = row.to_dict()
            failed = bool(params.pop(FAILED_COLUMN))
            objective_value = params.pop(OBJECTIVE_COLUMN)
            params = self._sanitize_params(params, distributions)

            if pd.isna(objective_value):
                continue

            trial_state = optuna.trial.TrialState.FAIL if failed else optuna.trial.TrialState.COMPLETE
            value = None if failed else float(objective_value)

            trial = optuna.trial.create_trial(
                distributions=distributions,
                params=params,
                value=value,
                state=trial_state,
            )
            study.add_trial(trial)
