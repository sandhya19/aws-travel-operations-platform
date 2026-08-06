"""Add a transactional outbox for workflow-start events."""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workflow_outbox_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "travel_request_id",
            sa.Uuid(),
            sa.ForeignKey("travel_requests.id"),
            nullable=False,
        ),
        sa.Column("event_type", sa.String(128), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_outbox_status_created", "workflow_outbox_events", ["status", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_outbox_status_created", table_name="workflow_outbox_events")
    op.drop_table("workflow_outbox_events")
