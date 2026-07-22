"""add_report_and_notification



Revision ID: e1c4a7d35f48

Revises: d9a6f3c24e32

Create Date: 2026-07-10 13:35:00.000000



"""



from typing import Sequence, Union



import sqlalchemy as sa

from alembic import op



revision: str = "e1c4a7d35f48"

down_revision: Union[str, None] = "d9a6f3c24e32"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None





def upgrade() -> None:

    """Add report and notification tables."""

    op.create_table(

        "report",

        sa.Column("portfolio_id", sa.Uuid(), nullable=True),

        sa.Column("report_type", sa.String(length=20), nullable=False),

        sa.Column("title", sa.String(length=255), nullable=False),

        sa.Column("markdown_content", sa.Text(), nullable=False),

        sa.Column("html_content", sa.Text(), nullable=False),

        sa.Column("period_start", sa.Date(), nullable=True),

        sa.Column("period_end", sa.Date(), nullable=True),

        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),

        sa.Column("id", sa.Uuid(), nullable=False),

        sa.ForeignKeyConstraint(["portfolio_id"], ["portfolio.id"]),

        sa.PrimaryKeyConstraint("id"),

    )

    op.create_index("ix_report_report_type", "report", ["report_type"], unique=False)

    op.create_index("ix_report_generated_at", "report", ["generated_at"], unique=False)

    op.create_index("ix_report_portfolio_id", "report", ["portfolio_id"], unique=False)



    op.create_table(

        "notification",

        sa.Column("channel", sa.String(length=20), nullable=False),

        sa.Column("notification_type", sa.String(length=50), nullable=False),

        sa.Column("title", sa.String(length=255), nullable=False),

        sa.Column("body", sa.Text(), nullable=False),

        sa.Column("status", sa.String(length=20), nullable=False),

        sa.Column("metadata_json", sa.JSON(), nullable=True),

        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),

        sa.Column("id", sa.Uuid(), nullable=False),

        sa.PrimaryKeyConstraint("id"),

    )

    op.create_index(

        "ix_notification_channel", "notification", ["channel"], unique=False

    )

    op.create_index("ix_notification_status", "notification", ["status"], unique=False)

    op.create_index(

        "ix_notification_created_at", "notification", ["created_at"], unique=False

    )





def downgrade() -> None:

    """Remove report and notification tables."""

    op.drop_index("ix_notification_created_at", table_name="notification")

    op.drop_index("ix_notification_status", table_name="notification")

    op.drop_index("ix_notification_channel", table_name="notification")

    op.drop_table("notification")

    op.drop_index("ix_report_portfolio_id", table_name="report")

    op.drop_index("ix_report_generated_at", table_name="report")

    op.drop_index("ix_report_report_type", table_name="report")

    op.drop_table("report")


