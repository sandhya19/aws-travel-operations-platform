"""Create a deployable Lambda zip from a Linux dependency directory."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
package_root = root / "dist" / "lambda-package"
archive = root / "dist" / "travel-operations-api.zip"

with ZipFile(archive, "w", ZIP_DEFLATED) as output:
    for path in package_root.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            output.write(path, path.relative_to(package_root))
