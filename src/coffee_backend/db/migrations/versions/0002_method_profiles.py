"""add method profiles

Revision ID: 0002_method_profiles
Revises: 0001_initial
Create Date: 2026-02-18
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_method_profiles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


METHOD_PROFILE_ROWS = [
    {
        "method_id": "v60",
        "variant_id": "v60_default",
        "schema_version": 1,
        "parameters": [
            {"name": "dose_g", "type": "float", "min": 12.0, "max": 20.0, "step": 0.5, "unit": "g", "default": 15.0, "description": "Coffee dose used for brewing."},
            {"name": "ratio", "type": "float", "min": 15.0, "max": 18.5, "step": 0.1, "unit": ":1", "default": 16.5, "description": "Coffee-to-water ratio."},
            {"name": "grind_step", "type": "int", "min": 1, "max": 40, "step": 1, "unit": "steps", "default": 20, "description": "Generic grinder step setting."},
            {"name": "temp_c", "type": "int", "min": 88, "max": 96, "step": 1, "unit": "°C", "default": 92, "description": "Brewing water temperature."},
            {"name": "total_time_s", "type": "int", "min": 150, "max": 240, "step": 5, "unit": "s", "default": 190, "description": "Total brew time."},
            {"name": "bloom_ratio", "type": "float", "min": 2.0, "max": 3.0, "step": 0.1, "unit": "x dose", "default": 2.5, "description": "Bloom water multiplier of coffee dose."},
            {"name": "bloom_s", "type": "int", "min": 25, "max": 50, "step": 5, "unit": "s", "default": 30, "description": "Bloom duration."},
            {"name": "pours", "type": "int", "min": 2, "max": 5, "step": 1, "unit": "count", "default": 3, "description": "Number of pours after bloom."},
        ],
    },
    {
        "method_id": "aeropress",
        "variant_id": "aeropress_standard",
        "schema_version": 1,
        "parameters": [
            {"name": "dose_g", "type": "float", "min": 12.0, "max": 20.0, "step": 0.5, "unit": "g", "default": 15.0, "description": "Coffee dose used for brewing."},
            {"name": "water_g", "type": "int", "min": 150, "max": 280, "step": 5, "unit": "g", "default": 230, "description": "Total brewing water mass."},
            {"name": "grind_step", "type": "int", "min": 1, "max": 40, "step": 1, "unit": "steps", "default": 18, "description": "Generic grinder step setting."},
            {"name": "temp_c", "type": "int", "min": 75, "max": 95, "step": 1, "unit": "°C", "default": 85, "description": "Brewing water temperature."},
            {"name": "steep_s", "type": "int", "min": 30, "max": 150, "step": 5, "unit": "s", "default": 60, "description": "Steeping duration before plunging."},
            {"name": "plunge_s", "type": "int", "min": 15, "max": 45, "step": 5, "unit": "s", "default": 25, "description": "Plunge duration."},
            {"name": "stir_count", "type": "int", "min": 0, "max": 20, "step": 1, "unit": "count", "default": 5, "description": "Number of stirs during agitation."},
        ],
    },
    {
        "method_id": "aeropress",
        "variant_id": "aeropress_inverted",
        "schema_version": 1,
        "parameters": [
            {"name": "dose_g", "type": "float", "min": 12.0, "max": 20.0, "step": 0.5, "unit": "g", "default": 15.0, "description": "Coffee dose used for brewing."},
            {"name": "water_g", "type": "int", "min": 150, "max": 280, "step": 5, "unit": "g", "default": 230, "description": "Total brewing water mass."},
            {"name": "grind_step", "type": "int", "min": 1, "max": 40, "step": 1, "unit": "steps", "default": 18, "description": "Generic grinder step setting."},
            {"name": "temp_c", "type": "int", "min": 75, "max": 95, "step": 1, "unit": "°C", "default": 85, "description": "Brewing water temperature."},
            {"name": "steep_s", "type": "int", "min": 30, "max": 150, "step": 5, "unit": "s", "default": 90, "description": "Steeping duration before plunging."},
            {"name": "plunge_s", "type": "int", "min": 15, "max": 45, "step": 5, "unit": "s", "default": 25, "description": "Plunge duration."},
            {"name": "stir_count", "type": "int", "min": 0, "max": 20, "step": 1, "unit": "count", "default": 8, "description": "Number of stirs during agitation."},
        ],
    },
]


def upgrade() -> None:
    op.create_table(
        "method_profiles",
        sa.Column("method_id", sa.String(length=50), nullable=False),
        sa.Column("variant_id", sa.String(length=100), nullable=True),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.UniqueConstraint(
            "method_id",
            "variant_id",
            "schema_version",
            name="uq_method_profiles_method_variant_version",
        ),
    )
    op.create_index(op.f("ix_method_profiles_method_id"), "method_profiles", ["method_id"], unique=False)
    op.create_index(op.f("ix_method_profiles_variant_id"), "method_profiles", ["variant_id"], unique=False)

    method_profiles = sa.table(
        "method_profiles",
        sa.column("method_id", sa.String),
        sa.column("variant_id", sa.String),
        sa.column("schema_version", sa.Integer),
        sa.column("parameters", sa.JSON),
    )
    op.bulk_insert(method_profiles, METHOD_PROFILE_ROWS)


def downgrade() -> None:
    op.drop_index(op.f("ix_method_profiles_variant_id"), table_name="method_profiles")
    op.drop_index(op.f("ix_method_profiles_method_id"), table_name="method_profiles")
    op.drop_table("method_profiles")
