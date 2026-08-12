"""Add durable, tenant-scoped agent sessions and append-only memory events."""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "travel_request_id", sa.Uuid(), sa.ForeignKey("travel_requests.id"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("travel_request_id"),
    )
    op.create_index(
        "ix_agent_sessions_tenant_user_created",
        "agent_sessions",
        ["tenant_id", "user_id", "created_at"],
    )
    op.create_index(
        "ix_agent_sessions_correlation", "agent_sessions", ["correlation_id"], unique=True
    )
    op.create_table(
        "agent_memory_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "agent_session_id", sa.Uuid(), sa.ForeignKey("agent_sessions.id"), nullable=False
        ),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column("actor_id", sa.String(255), nullable=False),
        sa.Column("source", sa.String(128), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_memory_events_session_created",
        "agent_memory_events",
        ["agent_session_id", "created_at"],
    )
    op.create_index(
        "ix_memory_events_tenant_correlation",
        "agent_memory_events",
        ["tenant_id", "correlation_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_memory_events_tenant_correlation", table_name="agent_memory_events")
    op.drop_index("ix_memory_events_session_created", table_name="agent_memory_events")
    op.drop_table("agent_memory_events")
    op.drop_index("ix_agent_sessions_correlation", table_name="agent_sessions")
    op.drop_index("ix_agent_sessions_tenant_user_created", table_name="agent_sessions")
    op.drop_table("agent_sessions")
