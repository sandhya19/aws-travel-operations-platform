"""Create the AgentCore Runtime direct-code ZIP after dependencies are staged."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

root = Path(__file__).resolve().parents[1]
source = root / "agent_runtime"
dependencies = root / "dist" / "agent-runtime-package"
archive = root / "dist" / "travel-operations-agent-runtime.zip"

if not dependencies.is_dir():
    message = (
        "Stage AgentCore dependencies in dist/agent-runtime-package before packaging; "
        "see docs/guides/deployment.md."
    )
    raise SystemExit(message)

with ZipFile(archive, "w", ZIP_DEFLATED) as output:
    for path in source.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            output.write(path, path.relative_to(source))
    for path in dependencies.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            output.write(path, path.relative_to(dependencies))
