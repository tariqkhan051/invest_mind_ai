"""add_scheduler_job_run



Revision ID: d9a6f3c24e32

Revises: c8f5e2b13d21

Create Date: 2026-07-10 13:25:00.000000



"""



from typing import Sequence, Union



import sqlalchemy as sa

from alembic import op



revision: str = "d9a6f3c24e32"

down_revision: Union[str, None] = "c8f5e2b13d21"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None





def upgrade() -> None:

    """Add scheduler_job_run table."""

    op.create_table(

        "scheduler_job_run",

        sa.Column("job_id", sa.String(length=50), nullable=False),

        sa.Column("job_name", sa.String(length=100), nullable=False),

        sa.Column("category", sa.String(length=50), nullable=False),

        sa.Column("status", sa.String(length=20), nullable=False),

        sa.Column("trigger", sa.String(length=20), nullable=False),

        sa.Column("message", sa.String(length=500), nullable=False),

        sa.Column("duration_ms", sa.Numeric(precision=12, scale=2), nullable=False),

        sa.Column("details", sa.JSON(), nullable=True),

        sa.Column("error_message", sa.Text(), nullable=True),

        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),

        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=False),

        sa.Column("id", sa.Uuid(), nullable=False),

        sa.PrimaryKeyConstraint("id"),

    )

    op.create_index(

        "ix_scheduler_job_run_job_id",

        "scheduler_job_run",

        ["job_id"],

        unique=False,

    )

    op.create_index(

        "ix_scheduler_job_run_started_at",

        "scheduler_job_run",

        ["started_at"],

        unique=False,

    )

    op.create_index(

        "ix_scheduler_job_run_status",

        "scheduler_job_run",

        ["status"],

        unique=False,

    )





def downgrade() -> None:

    """Remove scheduler_job_run table."""

    op.drop_index("ix_scheduler_job_run_status", table_name="scheduler_job_run")

    op.drop_index("ix_scheduler_job_run_started_at", table_name="scheduler_job_run")

    op.drop_index("ix_scheduler_job_run_job_id", table_name="scheduler_job_run")

    op.drop_table("scheduler_job_run")


