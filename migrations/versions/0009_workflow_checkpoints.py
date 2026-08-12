"""Add durable workflow recovery checkpoints."""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_checkpoints",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "agent_session_id", sa.Uuid(), sa.ForeignKey("agent_sessions.id"), nullable=False
        ),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("state", sa.String(64), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("agent_session_id", "state", name="uq_checkpoint_session_state"),
    )
    op.create_index(
        "ix_workflow_checkpoints_session_created",
        "workflow_checkpoints",
        ["agent_session_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_workflow_checkpoints_session_created", table_name="workflow_checkpoints")
    op.drop_table("workflow_checkpoints")
