"""Scope travel requests to the tenant that owns their durable memory."""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("travel_requests", sa.Column("tenant_id", sa.String(255), nullable=True))
    op.execute("UPDATE travel_requests SET tenant_id = 'default' WHERE tenant_id IS NULL")
    op.alter_column("travel_requests", "tenant_id", nullable=False)
    op.create_index(
        "ix_travel_requests_tenant_requester_status",
        "travel_requests",
        ["tenant_id", "requester_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_travel_requests_tenant_requester_status", table_name="travel_requests")
    op.drop_column("travel_requests", "tenant_id")
