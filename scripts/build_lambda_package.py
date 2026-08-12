"""Create a deployable Lambda zip from staged Linux dependencies and current source."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
package_root = root / "dist" / "lambda-package"
application_source = root / "src" / "travel_operations"
archive = root / "dist" / "travel-operations-api.zip"
temporary_archive = archive.with_suffix(".zip.tmp")

with ZipFile(temporary_archive, "w", ZIP_DEFLATED) as output:
    for path in package_root.rglob("*"):
        if (
            path.is_file()
            and "__pycache__" not in path.parts
            and "travel_operations" not in path.relative_to(package_root).parts
        ):
            output.write(path, path.relative_to(package_root))
    for path in application_source.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            output.write(path, path.relative_to(application_source.parent))

temporary_archive.replace(archive)
