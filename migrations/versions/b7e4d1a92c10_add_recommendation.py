"""add_recommendation

Revision ID: b7e4d1a92c10
Revises: a3f9c2e81b04
Create Date: 2026-07-10 12:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b7e4d1a92c10"
down_revision: Union[str, None] = "a3f9c2e81b04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add recommendation table."""
    op.create_table(
        "recommendation",
        sa.Column("portfolio_id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_type", sa.String(length=50), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("asset_id", sa.Uuid(), nullable=True),
        sa.Column("from_asset_id", sa.Uuid(), nullable=True),
        sa.Column("to_asset_id", sa.Uuid(), nullable=True),
        sa.Column("symbol", sa.String(length=50), nullable=True),
        sa.Column("from_symbol", sa.String(length=50), nullable=True),
        sa.Column("to_symbol", sa.String(length=50), nullable=True),
        sa.Column("recommended_amount", sa.Numeric(precision=19, scale=4), nullable=True),
        sa.Column("expected_return", sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column("expected_risk", sa.String(length=20), nullable=False),
        sa.Column("confidence", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("supporting_evidence", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("feedback_action", sa.String(length=50), nullable=True),
        sa.Column("feedback_notes", sa.Text(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["asset.id"]),
        sa.ForeignKeyConstraint(["from_asset_id"], ["asset.id"]),
        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolio.id"]),
        sa.ForeignKeyConstraint(["to_asset_id"], ["asset.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_recommendation_portfolio_id",
        "recommendation",
        ["portfolio_id"],
        unique=False,
    )
    op.create_index(
        "ix_recommendation_status",
        "recommendation",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_recommendation_generated_at",
        "recommendation",
        ["generated_at"],
        unique=False,
    )
    op.create_index(
        "ix_recommendation_priority",
        "recommendation",
        ["priority"],
        unique=False,
    )


def downgrade() -> None:
    """Remove recommendation table."""
    op.drop_index("ix_recommendation_priority", table_name="recommendation")
    op.drop_index("ix_recommendation_generated_at", table_name="recommendation")
    op.drop_index("ix_recommendation_status", table_name="recommendation")
    op.drop_index("ix_recommendation_portfolio_id", table_name="recommendation")
    op.drop_table("recommendation")
