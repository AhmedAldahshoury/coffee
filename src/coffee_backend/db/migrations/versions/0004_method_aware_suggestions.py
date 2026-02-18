"""add brew status and suggestion params snapshots

Revision ID: 0004_method_aware_suggestions
Revises: 0003_study_contexts
Create Date: 2026-02-18
"""

import sqlalchemy as sa
from alembic import op

revision = "0004_method_aware_suggestions"
down_revision = "0003_study_contexts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "brews",
        sa.Column(
            "status",
            sa.Enum("OK", "FAILED", name="brewstatus"),
            nullable=True,
        ),
    )
    op.execute(sa.text("UPDATE brews SET status = CASE WHEN failed THEN 'FAILED' ELSE 'OK' END"))
    op.alter_column("brews", "status", nullable=False)
    op.drop_column("brews", "failed")

    op.add_column("suggestions", sa.Column("actual_params", sa.JSON(), nullable=True))
    op.add_column("suggestions", sa.Column("suggested_params", sa.JSON(), nullable=True))
    op.execute(sa.text("UPDATE suggestions SET suggested_params = suggested_parameters"))
    op.alter_column("suggestions", "suggested_params", nullable=False)
    op.drop_column("suggestions", "suggested_parameters")


def downgrade() -> None:
    op.add_column(
        "suggestions",
        sa.Column("suggested_parameters", sa.JSON(), nullable=True),
    )
    op.execute(sa.text("UPDATE suggestions SET suggested_parameters = suggested_params"))
    op.alter_column("suggestions", "suggested_parameters", nullable=False)
    op.drop_column("suggestions", "suggested_params")
    op.drop_column("suggestions", "actual_params")

    op.add_column("brews", sa.Column("failed", sa.Boolean(), nullable=True))
    op.execute(sa.text("UPDATE brews SET failed = CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END"))
    op.alter_column("brews", "failed", nullable=False)
    op.drop_column("brews", "status")
    sa.Enum("OK", "FAILED", name="brewstatus").drop(op.get_bind(), checkfirst=True)
