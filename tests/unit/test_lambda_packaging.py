"""Deployment-artifact contracts."""

from pathlib import Path


def test_lambda_packager_uses_current_application_source() -> None:
    source = (Path(__file__).parents[2] / "scripts" / "build_lambda_package.py").read_text(
        encoding="utf-8"
    )

    assert 'application_source = root / "src" / "travel_operations"' in source
    assert '"travel_operations" not in path.relative_to(package_root).parts' in source
    assert "path.relative_to(application_source.parent)" in source
    assert "temporary_archive.replace(archive)" in source
