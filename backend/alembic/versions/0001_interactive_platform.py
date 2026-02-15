"""create interactive optimization tables

Revision ID: 0001
Revises:
Create Date: 2026-02-15
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_created_at", "users", ["created_at"], unique=False)

    op.create_table(
        "optimization_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("method", sa.String(length=32), nullable=False),
        sa.Column("selected_persons", sa.JSON(), nullable=False),
        sa.Column("best_score", sa.Float(), nullable=True),
        sa.Column("best_params", sa.JSON(), nullable=True),
        sa.Column("trial_count", sa.Integer(), nullable=False),
        sa.Column("n_trials", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_optimization_runs_user_id", "optimization_runs", ["user_id"], unique=False)

    op.create_table(
        "brews",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("coffee_amount", sa.Float(), nullable=False),
        sa.Column("grinder_setting_clicks", sa.Integer(), nullable=False),
        sa.Column("temperature_c", sa.Integer(), nullable=False),
        sa.Column("brew_time_seconds", sa.Integer(), nullable=False),
        sa.Column("press_time_seconds", sa.Integer(), nullable=False),
        sa.Column("anti_static_water_microliter", sa.Integer(), nullable=False),
        sa.Column("method", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_brews_user_id", "brews", ["user_id"], unique=False)
    op.create_index("ix_brews_score", "brews", ["score"], unique=False)

    op.create_table(
        "trials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("optimization_run_id", sa.Uuid(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column("trial_number", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["optimization_run_id"], ["optimization_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("optimization_run_id", "trial_number", name="uq_run_trial_number"),
    )
    op.create_index("ix_trials_run_state", "trials", ["optimization_run_id", "state"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_trials_run_state", table_name="trials")
    op.drop_table("trials")
    op.drop_index("ix_brews_score", table_name="brews")
    op.drop_index("ix_brews_user_id", table_name="brews")
    op.drop_table("brews")
    op.drop_index("ix_optimization_runs_user_id", table_name="optimization_runs")
    op.drop_table("optimization_runs")
    op.drop_index("ix_users_created_at", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
