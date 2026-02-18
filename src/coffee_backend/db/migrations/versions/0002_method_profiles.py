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


def parameter(
    name: str,
    value_type: str,
    minimum: int | float,
    maximum: int | float,
    step: int | float,
    unit: str,
    default: int | float,
    description: str,
) -> dict[str, object]:
    return {
        "name": name,
        "type": value_type,
        "min": minimum,
        "max": maximum,
        "step": step,
        "unit": unit,
        "default": default,
        "description": description,
    }


METHOD_PROFILE_ROWS = [
    {
        "method_id": "v60",
        "variant_id": "v60_default",
        "schema_version": 1,
        "parameters": [
            parameter(
                "dose_g",
                "float",
                12.0,
                20.0,
                0.5,
                "g",
                15.0,
                "Coffee dose used for brewing.",
            ),
            parameter("ratio", "float", 15.0, 18.5, 0.1, ":1", 16.5, "Coffee-to-water ratio."),
            parameter(
                "grind_step",
                "int",
                1,
                40,
                1,
                "steps",
                20,
                "Generic grinder step setting.",
            ),
            parameter("temp_c", "int", 88, 96, 1, "°C", 92, "Brewing water temperature."),
            parameter("total_time_s", "int", 150, 240, 5, "s", 190, "Total brew time."),
            parameter(
                "bloom_ratio",
                "float",
                2.0,
                3.0,
                0.1,
                "x dose",
                2.5,
                "Bloom water multiplier of coffee dose.",
            ),
            parameter("bloom_s", "int", 25, 50, 5, "s", 30, "Bloom duration."),
            parameter(
                "pours",
                "int",
                2,
                5,
                1,
                "count",
                3,
                "Number of pours after bloom.",
            ),
        ],
    },
    {
        "method_id": "aeropress",
        "variant_id": "aeropress_standard",
        "schema_version": 1,
        "parameters": [
            parameter(
                "dose_g",
                "float",
                12.0,
                20.0,
                0.5,
                "g",
                15.0,
                "Coffee dose used for brewing.",
            ),
            parameter("water_g", "int", 150, 280, 5, "g", 230, "Total brewing water mass."),
            parameter(
                "grind_step",
                "int",
                1,
                40,
                1,
                "steps",
                18,
                "Generic grinder step setting.",
            ),
            parameter("temp_c", "int", 75, 95, 1, "°C", 85, "Brewing water temperature."),
            parameter(
                "steep_s",
                "int",
                30,
                150,
                5,
                "s",
                60,
                "Steeping duration before plunging.",
            ),
            parameter("plunge_s", "int", 15, 45, 5, "s", 25, "Plunge duration."),
            parameter(
                "stir_count",
                "int",
                0,
                20,
                1,
                "count",
                5,
                "Number of stirs during agitation.",
            ),
        ],
    },
    {
        "method_id": "aeropress",
        "variant_id": "aeropress_inverted",
        "schema_version": 1,
        "parameters": [
            parameter(
                "dose_g",
                "float",
                12.0,
                20.0,
                0.5,
                "g",
                15.0,
                "Coffee dose used for brewing.",
            ),
            parameter("water_g", "int", 150, 280, 5, "g", 230, "Total brewing water mass."),
            parameter(
                "grind_step",
                "int",
                1,
                40,
                1,
                "steps",
                18,
                "Generic grinder step setting.",
            ),
            parameter("temp_c", "int", 75, 95, 1, "°C", 85, "Brewing water temperature."),
            parameter(
                "steep_s",
                "int",
                30,
                150,
                5,
                "s",
                90,
                "Steeping duration before plunging.",
            ),
            parameter("plunge_s", "int", 15, 45, 5, "s", 25, "Plunge duration."),
            parameter(
                "stir_count",
                "int",
                0,
                20,
                1,
                "count",
                8,
                "Number of stirs during agitation.",
            ),
        ],
    },
]


def upgrade() -> None:
    op.create_table(
        "method_profiles",
        sa.Column("method_id", sa.String(length=50), nullable=False),
        sa.Column("variant_id", sa.String(length=100), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("method_id", "variant_id", "schema_version"),
    )
    op.create_index(
        op.f("ix_method_profiles_method_id"),
        "method_profiles",
        ["method_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_method_profiles_variant_id"),
        "method_profiles",
        ["variant_id"],
        unique=False,
    )

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
