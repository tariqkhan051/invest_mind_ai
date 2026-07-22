"""add_learning_record



Revision ID: c8f5e2b13d21

Revises: b7e4d1a92c10

Create Date: 2026-07-10 13:10:00.000000



"""



from typing import Sequence, Union



import sqlalchemy as sa

from alembic import op



revision: str = "c8f5e2b13d21"

down_revision: Union[str, None] = "b7e4d1a92c10"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None





def upgrade() -> None:

    """Add learning_record and learning_weight tables."""

    op.create_table(

        "learning_record",

        sa.Column("recommendation_id", sa.Uuid(), nullable=False),

        sa.Column("portfolio_snapshot_id", sa.Uuid(), nullable=True),

        sa.Column("strategy_id", sa.String(length=50), nullable=True),

        sa.Column("outcome", sa.String(length=50), nullable=False),

        sa.Column("expected_return", sa.Numeric(precision=8, scale=4), nullable=True),

        sa.Column("actual_return", sa.Numeric(precision=8, scale=4), nullable=True),

        sa.Column("prediction_error", sa.Numeric(precision=8, scale=4), nullable=True),

        sa.Column("learning_score", sa.Numeric(precision=8, scale=4), nullable=True),

        sa.Column(

            "confidence_adjustment", sa.Numeric(precision=8, scale=4), nullable=True

        ),

        sa.Column("reward", sa.Numeric(precision=8, scale=4), nullable=True),

        sa.Column("penalty", sa.Numeric(precision=8, scale=4), nullable=True),

        sa.Column("feedback", sa.String(length=50), nullable=True),

        sa.Column("evaluated_at", sa.DateTime(timezone=True), nullable=True),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),

        sa.Column("id", sa.Uuid(), nullable=False),

        sa.ForeignKeyConstraint(["portfolio_snapshot_id"], ["portfolio_snapshot.id"]),

        sa.ForeignKeyConstraint(["recommendation_id"], ["recommendation.id"]),

        sa.PrimaryKeyConstraint("id"),

    )

    op.create_index(

        "ix_learning_record_recommendation_id",

        "learning_record",

        ["recommendation_id"],

        unique=False,

    )

    op.create_index(

        "ix_learning_record_strategy_id",

        "learning_record",

        ["strategy_id"],

        unique=False,

    )

    op.create_index(

        "ix_learning_record_outcome",

        "learning_record",

        ["outcome"],

        unique=False,

    )

    op.create_index(

        "ix_learning_record_evaluated_at",

        "learning_record",

        ["evaluated_at"],

        unique=False,

    )



    op.create_table(

        "learning_weight",

        sa.Column("strategy_key", sa.String(length=50), nullable=False),

        sa.Column("weight_multiplier", sa.Numeric(precision=8, scale=4), nullable=False),

        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),

        sa.Column("id", sa.Uuid(), nullable=False),

        sa.PrimaryKeyConstraint("id"),

        sa.UniqueConstraint("strategy_key"),

    )

    op.create_index(

        "ix_learning_weight_strategy_key",

        "learning_weight",

        ["strategy_key"],

        unique=True,

    )





def downgrade() -> None:

    """Remove learning tables."""

    op.drop_index("ix_learning_weight_strategy_key", table_name="learning_weight")

    op.drop_table("learning_weight")

    op.drop_index("ix_learning_record_evaluated_at", table_name="learning_record")

    op.drop_index("ix_learning_record_outcome", table_name="learning_record")

    op.drop_index("ix_learning_record_strategy_id", table_name="learning_record")

    op.drop_index("ix_learning_record_recommendation_id", table_name="learning_record")

    op.drop_table("learning_record")


