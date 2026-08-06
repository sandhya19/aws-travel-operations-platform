"""Create versioned knowledge chunks for grounded retrieval.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the versioned chunk store before evaluation-history revisions."""
    op.create_table(
        "knowledge_chunks",
        sa.Column("document_id", sa.String(64), nullable=False),
        sa.Column("chunk_id", sa.String(32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source_uri", sa.Text(), nullable=False),
        sa.Column("version", sa.String(64), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("document_id", "chunk_id", "version"),
    )
    op.execute("ALTER TABLE knowledge_chunks ADD COLUMN embedding VECTOR(1024)")
    op.create_index(
        "ix_knowledge_chunks_document_version", "knowledge_chunks", ["document_id", "version"]
    )


def downgrade() -> None:
    """Remove the chunk store and its vector data."""
    op.drop_table("knowledge_chunks")
