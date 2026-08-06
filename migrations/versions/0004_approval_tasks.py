"""Add callback-token approval tasks for the travel workflow."""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "approval_tasks",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "travel_request_id", sa.Uuid(), sa.ForeignKey("travel_requests.id"), nullable=False
        ),
        sa.Column("task_token", sa.Text(), nullable=False, unique=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("approver_id", sa.String(255), nullable=True),
    )
    op.create_index(
        "ix_approval_tasks_request_status", "approval_tasks", ["travel_request_id", "status"]
    )


def downgrade() -> None:
    op.drop_table("approval_tasks")
