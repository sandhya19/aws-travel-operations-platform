"""Add tenant-owned document versions and scoped chunk metadata."""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "knowledge_documents",
        sa.Column("document_id", sa.String(64), primary_key=True),
        sa.Column("tenant_id", sa.String(255), nullable=False),
        sa.Column("source_key", sa.Text(), nullable=False),
        sa.Column("version", sa.String(64), nullable=False),
        sa.Column("content_type", sa.String(64), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "source_key", "version"),
    )
    op.create_index(
        "ix_knowledge_documents_tenant_source",
        "knowledge_documents",
        ["tenant_id", "source_key"],
    )
    op.add_column("knowledge_chunks", sa.Column("tenant_id", sa.String(255), nullable=True))
    op.add_column("knowledge_chunks", sa.Column("page_number", sa.Integer(), nullable=True))
    op.execute("UPDATE knowledge_chunks SET tenant_id = 'default' WHERE tenant_id IS NULL")
    op.execute("UPDATE knowledge_chunks SET page_number = 1 WHERE page_number IS NULL")
    op.alter_column("knowledge_chunks", "tenant_id", nullable=False)
    op.alter_column("knowledge_chunks", "page_number", nullable=False)
    op.create_index(
        "ix_knowledge_chunks_tenant_document_version",
        "knowledge_chunks",
        ["tenant_id", "document_id", "version"],
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_chunks_tenant_document_version", table_name="knowledge_chunks")
    op.drop_column("knowledge_chunks", "page_number")
    op.drop_column("knowledge_chunks", "tenant_id")
    op.drop_index("ix_knowledge_documents_tenant_source", table_name="knowledge_documents")
    op.drop_table("knowledge_documents")
