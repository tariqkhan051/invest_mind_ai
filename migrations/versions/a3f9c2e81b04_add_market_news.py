"""add_market_news

Revision ID: a3f9c2e81b04
Revises: dd74b175d256
Create Date: 2026-07-10 12:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3f9c2e81b04"
down_revision: Union[str, None] = "dd74b175d256"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add market_news table."""
    op.create_table(
        "market_news",
        sa.Column("headline", sa.String(length=500), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("publisher", sa.String(length=255), nullable=True),
        sa.Column("publication_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("sentiment", sa.String(length=20), nullable=False),
        sa.Column("sentiment_score", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("url", name="uq_market_news_url"),
    )
    op.create_index(
        "ix_market_news_publication_time",
        "market_news",
        ["publication_time"],
        unique=False,
    )
    op.create_index(
        "ix_market_news_category",
        "market_news",
        ["category"],
        unique=False,
    )
    op.create_index(
        "ix_market_news_country",
        "market_news",
        ["country"],
        unique=False,
    )


def downgrade() -> None:
    """Remove market_news table."""
    op.drop_index("ix_market_news_country", table_name="market_news")
    op.drop_index("ix_market_news_category", table_name="market_news")
    op.drop_index("ix_market_news_publication_time", table_name="market_news")
    op.drop_table("market_news")
