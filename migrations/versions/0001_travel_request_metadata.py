"""Create travel metadata and vector column."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "travel_requests",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("requester_id", sa.String(255), nullable=False),
        sa.Column("destination_country", sa.String(2), nullable=False),
        sa.Column("departure_date", sa.Date(), nullable=False),
        sa.Column("return_date", sa.Date(), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
    )
    op.create_index(
        "ix_travel_requests_requester_status", "travel_requests", ["requester_id", "status"]
    )
    op.execute("ALTER TABLE travel_requests ADD COLUMN embedding VECTOR(1536)")


def downgrade() -> None:
    op.drop_table("travel_requests")
