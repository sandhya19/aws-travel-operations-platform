"""Add role metadata for ACL-filtered knowledge retrieval."""

import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_document_access",
        sa.Column(
            "document_id",
            sa.String(64),
            sa.ForeignKey("knowledge_documents.document_id"),
            primary_key=True,
        ),
        sa.Column("role", sa.String(255), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("knowledge_document_access")
