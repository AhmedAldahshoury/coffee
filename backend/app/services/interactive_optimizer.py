from __future__ import annotations

import json
import uuid
from collections.abc import Generator

import optuna
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.persistence import Brew, OptimizationRun, Trial, User


class InteractiveOptimizerService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def start_run(self, user: User, selected_persons: list[str], method: str, n_trials: int) -> OptimizationRun:
        run = OptimizationRun(
            user_id=user.id,
            status="running",
            method=method,
            selected_persons=selected_persons,
            n_trials=n_trials,
            trial_count=0,
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        self._suggest_next_trial(run)
        return run

    def submit_score(self, run: OptimizationRun, trial_id: int, score: float) -> OptimizationRun:
        trial = self.db.scalar(
            select(Trial).where(Trial.id == trial_id, Trial.optimization_run_id == run.id)
        )
        if not trial:
            raise ValueError("Trial not found")
        if trial.state == "completed":
            raise ValueError("Trial score already submitted")

        trial.score = score
        trial.state = "completed"

        params = trial.parameters
        brew = Brew(
            user_id=run.user_id,
            method=run.method,
            score=score,
            coffee_amount=float(params["coffee_amount"]),
            grinder_setting_clicks=int(params["grinder_setting_clicks"]),
            temperature_c=int(params["temperature_c"]),
            brew_time_seconds=int(params["brew_time_seconds"]),
            press_time_seconds=int(params["press_time_seconds"]),
            anti_static_water_microliter=int(params["anti_static_water_microliter"]),
        )
        self.db.add(brew)

        run.trial_count += 1
        if run.best_score is None or score > run.best_score:
            run.best_score = score
            run.best_params = params

        if run.trial_count >= run.n_trials:
            run.status = "finished"
        else:
            self._suggest_next_trial(run)

        self.db.commit()
        self.db.refresh(run)
        return run

    def list_runs(self, user: User) -> list[OptimizationRun]:
        return list(
            self.db.scalars(
                select(OptimizationRun)
                .where(OptimizationRun.user_id == user.id)
                .order_by(OptimizationRun.created_at.desc())
            )
        )

    def get_run(self, run_id: uuid.UUID, user: User) -> OptimizationRun | None:
        return self.db.scalar(
            select(OptimizationRun).where(OptimizationRun.id == run_id, OptimizationRun.user_id == user.id)
        )

    def stream_events(self, run: OptimizationRun) -> Generator[str, None, None]:
        self.db.refresh(run)
        last_trial = self._latest_trial(run.id)
        payload = {
            "trial_number": last_trial.trial_number if last_trial else run.trial_count,
            "best_score": run.best_score,
            "best_parameters": run.best_params,
            "last_trial_parameters": last_trial.parameters if last_trial else None,
            "last_trial_score": last_trial.score if last_trial else None,
            "run_status": run.status,
        }
        yield f"data: {json.dumps(payload)}\n\n"

    def _latest_trial(self, run_id: uuid.UUID) -> Trial | None:
        return self.db.scalar(
            select(Trial)
            .where(Trial.optimization_run_id == run_id)
            .order_by(Trial.trial_number.desc())
            .limit(1)
        )

    def _suggest_next_trial(self, run: OptimizationRun) -> Trial:
        study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
        completed_trials = list(
            self.db.scalars(
                select(Trial)
                .where(Trial.optimization_run_id == run.id, Trial.state == "completed")
                .order_by(Trial.trial_number.asc())
            )
        )

        distributions = {
            "coffee_amount": optuna.distributions.FloatDistribution(12, 25, step=0.5),
            "grinder_setting_clicks": optuna.distributions.IntDistribution(5, 25),
            "temperature_c": optuna.distributions.IntDistribution(75, 95),
            "brew_time_seconds": optuna.distributions.IntDistribution(60, 300),
            "press_time_seconds": optuna.distributions.IntDistribution(10, 120),
            "anti_static_water_microliter": optuna.distributions.IntDistribution(0, 500),
        }

        for item in completed_trials:
            study.add_trial(
                optuna.trial.create_trial(
                    params=item.parameters,
                    distributions=distributions,
                    value=float(item.score),
                    state=optuna.trial.TrialState.COMPLETE,
                )
            )

        trial = study.ask(distributions)
        db_trial = Trial(
            optimization_run_id=run.id,
            parameters=trial.params,
            state="suggested",
            trial_number=len(completed_trials) + 1,
        )
        self.db.add(db_trial)
        self.db.flush()
        return db_trial
