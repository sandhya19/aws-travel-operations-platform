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
