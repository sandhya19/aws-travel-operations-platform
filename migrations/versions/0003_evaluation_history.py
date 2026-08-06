import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evaluation_history",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("prompt_version", sa.String(64), nullable=False),
        sa.Column("dataset_case_id", sa.String(128), nullable=False),
        sa.Column("groundedness", sa.Float(), nullable=False),
        sa.Column("faithfulness", sa.Float(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("citation_accuracy", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("evaluation_history")
