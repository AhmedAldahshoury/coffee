"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-17
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "beans",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("roaster", sa.String(length=255), nullable=True),
        sa.Column("origin", sa.String(length=255), nullable=True),
        sa.Column("process", sa.String(length=255), nullable=True),
        sa.Column("roast_level", sa.String(length=50), nullable=True),
        sa.Column("roast_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_beans_user_id"), "beans", ["user_id"], unique=False)

    op.create_table(
        "equipment",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("grinder_model", sa.String(length=255), nullable=True),
        sa.Column("filter_type", sa.String(length=255), nullable=True),
        sa.Column("kettle", sa.String(length=255), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_equipment_method"), "equipment", ["method"], unique=False)
    op.create_index(op.f("ix_equipment_user_id"), "equipment", ["user_id"], unique=False)

    op.create_table(
        "recipes",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("parameter_schema", sa.JSON(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recipes_method"), "recipes", ["method"], unique=False)
    op.create_index(op.f("ix_recipes_user_id"), "recipes", ["user_id"], unique=False)

    op.create_table(
        "brews",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("bean_id", sa.Uuid(), nullable=True),
        sa.Column("recipe_id", sa.Uuid(), nullable=True),
        sa.Column("equipment_id", sa.Uuid(), nullable=True),
        sa.Column("method", sa.String(length=50), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("extra_data", sa.JSON(), nullable=True),
        sa.Column("brewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("failed", sa.Boolean(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("import_hash", sa.String(length=64), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["bean_id"], ["beans.id"]),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"]),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("import_hash"),
    )
    op.create_index(op.f("ix_brews_brewed_at"), "brews", ["brewed_at"], unique=False)
    op.create_index(op.f("ix_brews_method"), "brews", ["method"], unique=False)
    op.create_index(op.f("ix_brews_user_id"), "brews", ["user_id"], unique=False)

    op.create_table(
        "suggestions",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("brew_id", sa.Uuid(), nullable=True),
        sa.Column("study_key", sa.String(length=255), nullable=False),
        sa.Column("trial_number", sa.Integer(), nullable=False),
        sa.Column("suggested_parameters", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["brew_id"], ["brews.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_suggestions_status"), "suggestions", ["status"], unique=False)
    op.create_index(op.f("ix_suggestions_study_key"), "suggestions", ["study_key"], unique=False)
    op.create_index(op.f("ix_suggestions_user_id"), "suggestions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_suggestions_user_id"), table_name="suggestions")
    op.drop_index(op.f("ix_suggestions_study_key"), table_name="suggestions")
    op.drop_index(op.f("ix_suggestions_status"), table_name="suggestions")
    op.drop_table("suggestions")
    op.drop_index(op.f("ix_brews_user_id"), table_name="brews")
    op.drop_index(op.f("ix_brews_method"), table_name="brews")
    op.drop_index(op.f("ix_brews_brewed_at"), table_name="brews")
    op.drop_table("brews")
    op.drop_index(op.f("ix_recipes_user_id"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_method"), table_name="recipes")
    op.drop_table("recipes")
    op.drop_index(op.f("ix_equipment_user_id"), table_name="equipment")
    op.drop_index(op.f("ix_equipment_method"), table_name="equipment")
    op.drop_table("equipment")
    op.drop_index(op.f("ix_beans_user_id"), table_name="beans")
    op.drop_table("beans")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
