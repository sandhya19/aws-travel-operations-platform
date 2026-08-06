"""Append prepared dependencies to the deployable Lambda archive."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
source = root / "dist" / "lambda-extra"
archive = root / "dist" / "travel-operations-api.zip"

with ZipFile(archive, "a", ZIP_DEFLATED) as output:
    for path in source.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            output.write(path, path.relative_to(source))
