"""Add immutable travel-case plans and tool-execution provenance."""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_plans",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "agent_session_id", sa.Uuid(), sa.ForeignKey("agent_sessions.id"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("plan_type", sa.String(128), nullable=False),
        sa.Column("plan_version", sa.String(64), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_agent_plans_session_created", "agent_plans", ["agent_session_id", "created_at"]
    )
    op.create_table(
        "tool_executions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "agent_session_id", sa.Uuid(), sa.ForeignKey("agent_sessions.id"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("tool_name", sa.String(128), nullable=False),
        sa.Column("invocation_id", sa.String(255), nullable=False, unique=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("input_payload", sa.Text(), nullable=False),
        sa.Column("output_payload", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_tool_executions_session_started", "tool_executions", ["agent_session_id", "started_at"]
    )
    op.create_index(
        "ix_tool_executions_tenant_correlation",
        "tool_executions",
        ["tenant_id", "correlation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_tool_executions_tenant_correlation", table_name="tool_executions")
    op.drop_index("ix_tool_executions_session_started", table_name="tool_executions")
    op.drop_table("tool_executions")
    op.drop_index("ix_agent_plans_session_created", table_name="agent_plans")
    op.drop_table("agent_plans")
