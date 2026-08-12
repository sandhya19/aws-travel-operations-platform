"""Migration contract checks for the empty-database upgrade chain."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_evaluation_history_has_a_resolvable_predecessor() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    evaluation_revision = scripts.get_revision("0003")

    assert evaluation_revision is not None
    assert evaluation_revision.down_revision == "0002"
    assert scripts.get_revision("0002") is not None


def test_outbox_retry_and_approval_audit_follow_the_outbox() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    outbox_revision = scripts.get_revision("0006")

    assert outbox_revision is not None
    assert outbox_revision.down_revision == "0005"


def test_agent_memory_follows_approval_audit() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    memory_revision = scripts.get_revision("0007")

    assert memory_revision is not None
    assert memory_revision.down_revision == "0006"


def test_agent_provenance_follows_memory() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    provenance_revision = scripts.get_revision("0008")

    assert provenance_revision is not None
    assert provenance_revision.down_revision == "0007"


def test_workflow_checkpoints_follow_agent_provenance() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    checkpoint_revision = scripts.get_revision("0009")

    assert checkpoint_revision is not None
    assert checkpoint_revision.down_revision == "0008"


def test_memory_lifecycle_follows_workflow_checkpoints() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    lifecycle_revision = scripts.get_revision("0010")

    assert lifecycle_revision is not None
    assert lifecycle_revision.down_revision == "0009"


def test_travel_request_tenant_scope_follows_memory_lifecycle() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    tenancy_revision = scripts.get_revision("0011")

    assert tenancy_revision is not None
    assert tenancy_revision.down_revision == "0010"


def test_secure_knowledge_documents_follow_tenant_scope() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    ingestion_revision = scripts.get_revision("0012")

    assert ingestion_revision is not None
    assert ingestion_revision.down_revision == "0011"


def test_knowledge_document_access_follows_secure_ingestion() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)
    access_revision = scripts.get_revision("0013")

    assert access_revision is not None
    assert access_revision.down_revision == "0012"
