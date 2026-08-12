"""Add retention expiry and immutable memory lifecycle records."""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "agent_sessions", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "agent_sessions", sa.Column("expired_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.execute("UPDATE agent_sessions SET expires_at = created_at WHERE expires_at IS NULL")
    op.alter_column("agent_sessions", "expires_at", nullable=False)
    op.create_table(
        "memory_lifecycle_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("agent_session_id", sa.Uuid(), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_memory_lifecycle_correlation",
        "memory_lifecycle_records",
        ["correlation_id", "occurred_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_memory_lifecycle_correlation", table_name="memory_lifecycle_records")
    op.drop_table("memory_lifecycle_records")
    op.drop_column("agent_sessions", "expired_at")
    op.drop_column("agent_sessions", "expires_at")
