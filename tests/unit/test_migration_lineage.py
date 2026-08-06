"""Alembic lineage checks that do not require a running database."""

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


def test_migration_history_has_one_linear_head() -> None:
    config = Config(str(Path(__file__).parents[2] / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)

    assert scripts.get_heads() == ["0006"]
    assert [revision.revision for revision in scripts.walk_revisions()] == [
        "0006",
        "0005",
        "0004",
        "0003",
        "0002",
        "0001",
    ]
