"""add study contexts and scoped suggestions

Revision ID: 0003_study_contexts
Revises: 0002_method_profiles
Create Date: 2026-02-18
"""

from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision = "0003_study_contexts"
down_revision = "0002_method_profiles"
branch_labels = None
depends_on = None


def _default_variant(method_id: str) -> str:
    if method_id == "aeropress":
        return "aeropress_standard"
    if method_id in {"pourover", "v60"}:
        return "v60_default"
    return f"{method_id}_default"


def _build_study_key(
    user_id: str,
    method_id: str,
    variant_id: str,
    bean_id: str | None,
    equipment_id: str | None,
) -> str:
    return (
        f"u:{user_id}|m:{method_id}|v:{variant_id}|"
        f"b:{bean_id or 'none'}|e:{equipment_id or 'none'}"
    )


def upgrade() -> None:
    op.add_column("brews", sa.Column("variant_id", sa.String(length=100), nullable=True))

    op.create_table(
        "study_contexts",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("method_id", sa.String(length=50), nullable=False),
        sa.Column("variant_id", sa.String(length=100), nullable=False),
        sa.Column("bean_id", sa.Uuid(), nullable=True),
        sa.Column("equipment_id", sa.Uuid(), nullable=True),
        sa.Column("study_key", sa.String(length=255), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["bean_id"], ["beans.id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("study_key", name="uq_study_context_study_key"),
        sa.UniqueConstraint(
            "user_id",
            "method_id",
            "variant_id",
            "bean_id",
            "equipment_id",
            name="uq_study_context_scope",
        ),
    )
    op.create_index(op.f("ix_study_contexts_user_id"), "study_contexts", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_study_contexts_method_id"), "study_contexts", ["method_id"], unique=False
    )
    op.create_index(
        op.f("ix_study_contexts_variant_id"), "study_contexts", ["variant_id"], unique=False
    )
    op.create_index(
        op.f("ix_study_contexts_study_key"), "study_contexts", ["study_key"], unique=False
    )

    op.add_column("suggestions", sa.Column("study_context_id", sa.Uuid(), nullable=True))
    op.create_index(
        op.f("ix_suggestions_study_context_id"), "suggestions", ["study_context_id"], unique=False
    )
    op.create_foreign_key(
        "fk_suggestions_study_context_id",
        "suggestions",
        "study_contexts",
        ["study_context_id"],
        ["id"],
        ondelete="CASCADE",
    )

    connection = op.get_bind()

    brews = connection.execute(sa.text("SELECT id, method FROM brews")).fetchall()
    for brew in brews:
        connection.execute(
            sa.text("UPDATE brews SET variant_id = :variant_id WHERE id = :brew_id"),
            {"variant_id": _default_variant(brew.method), "brew_id": brew.id},
        )

    suggestions = connection.execute(
        sa.text(
            """
            SELECT id, user_id, study_key
            FROM suggestions
            """
        )
    ).fetchall()

    for suggestion in suggestions:
        raw = suggestion.study_key
        parsed: dict[str, str | None] = {
            "method_id": None,
            "variant_id": None,
            "bean_id": None,
            "equipment_id": None,
        }

        if "|" in raw:
            parts = dict(item.split(":", 1) for item in raw.split("|"))
            parsed["method_id"] = parts.get("m")
            parsed["variant_id"] = parts.get("v")
            parsed["bean_id"] = parts.get("b")
            parsed["equipment_id"] = parts.get("e")
        else:
            parts = dict(item.split(":", 1) for item in raw.split(":"))
            parsed["method_id"] = parts.get("m")
            parsed["bean_id"] = parts.get("b")
            parsed["equipment_id"] = parts.get("e")

        method_id = str(parsed["method_id"] or "aeropress")
        variant_id = str(parsed["variant_id"] or _default_variant(method_id))
        bean_id = None if parsed["bean_id"] in {None, "none"} else parsed["bean_id"]
        equipment_id = None if parsed["equipment_id"] in {None, "none"} else parsed["equipment_id"]

        study_key = _build_study_key(
            str(suggestion.user_id),
            method_id,
            variant_id,
            bean_id,
            equipment_id,
        )

        existing = connection.execute(
            sa.text("SELECT id FROM study_contexts WHERE study_key = :study_key"),
            {"study_key": study_key},
        ).fetchone()

        if existing is None:
            context_id = uuid4()
            connection.execute(
                sa.text(
                    """
                    INSERT INTO study_contexts (
                        id,
                        user_id,
                        method_id,
                        variant_id,
                        bean_id,
                        equipment_id,
                        study_key
                    )
                    VALUES (
                        :id,
                        :user_id,
                        :method_id,
                        :variant_id,
                        :bean_id,
                        :equipment_id,
                        :study_key
                    )
                    """
                ),
                {
                    "id": context_id,
                    "user_id": suggestion.user_id,
                    "method_id": method_id,
                    "variant_id": variant_id,
                    "bean_id": bean_id,
                    "equipment_id": equipment_id,
                    "study_key": study_key,
                },
            )
        else:
            context_id = existing.id

        connection.execute(
            sa.text(
                """
                UPDATE suggestions
                SET study_context_id = :study_context_id,
                    study_key = :study_key
                WHERE id = :suggestion_id
                """
            ),
            {
                "study_context_id": context_id,
                "study_key": study_key,
                "suggestion_id": suggestion.id,
            },
        )

    op.alter_column("brews", "variant_id", existing_type=sa.String(length=100), nullable=False)
    op.alter_column("suggestions", "study_context_id", existing_type=sa.Uuid(), nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_suggestions_study_context_id", "suggestions", type_="foreignkey")
    op.drop_index(op.f("ix_suggestions_study_context_id"), table_name="suggestions")
    op.drop_column("suggestions", "study_context_id")

    op.drop_index(op.f("ix_study_contexts_study_key"), table_name="study_contexts")
    op.drop_index(op.f("ix_study_contexts_variant_id"), table_name="study_contexts")
    op.drop_index(op.f("ix_study_contexts_method_id"), table_name="study_contexts")
    op.drop_index(op.f("ix_study_contexts_user_id"), table_name="study_contexts")
    op.drop_table("study_contexts")

    op.drop_column("brews", "variant_id")
