"""add_market_macro_indicator

Revision ID: dd74b175d256
Revises: 4a18fbab5681
Create Date: 2026-07-10 10:56:27.110410

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dd74b175d256"
down_revision: Union[str, None] = "4a18fbab5681"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add market_macro_indicator table."""
    op.create_table(
        "market_macro_indicator",
        sa.Column("indicator_name", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("release_date", sa.Date(), nullable=False),
        sa.Column("frequency", sa.String(length=50), nullable=True),
        sa.Column("forecast_value", sa.Numeric(precision=19, scale=6), nullable=True),
        sa.Column("actual_value", sa.Numeric(precision=19, scale=6), nullable=False),
        sa.Column("previous_value", sa.Numeric(precision=19, scale=6), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("importance", sa.String(length=50), nullable=True),
        sa.Column("trend", sa.String(length=50), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("quality_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "indicator_name",
            "release_date",
            "country",
            name="uq_macro_indicator_date_country",
        ),
    )
    op.create_index(
        "ix_macro_indicator_name",
        "market_macro_indicator",
        ["indicator_name"],
        unique=False,
    )
    op.create_index(
        "ix_macro_release_date",
        "market_macro_indicator",
        ["release_date"],
        unique=False,
    )
    op.create_index(
        "ix_macro_country",
        "market_macro_indicator",
        ["country"],
        unique=False,
    )


def downgrade() -> None:
    """Remove market_macro_indicator table."""
    op.drop_index("ix_macro_country", table_name="market_macro_indicator")
    op.drop_index("ix_macro_release_date", table_name="market_macro_indicator")
    op.drop_index("ix_macro_indicator_name", table_name="market_macro_indicator")
    op.drop_table("market_macro_indicator")
