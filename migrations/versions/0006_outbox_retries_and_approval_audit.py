"""Add outbox retry state and immutable approval decisions."""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workflow_outbox_events",
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("workflow_outbox_events", sa.Column("last_error", sa.Text(), nullable=True))
    op.create_table(
        "approval_decisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "approval_task_id", sa.Uuid(), sa.ForeignKey("approval_tasks.id"), nullable=False
        ),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("approver_id", sa.String(255), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("approval_decisions")
    op.drop_column("workflow_outbox_events", "last_error")
    op.drop_column("workflow_outbox_events", "attempts")
