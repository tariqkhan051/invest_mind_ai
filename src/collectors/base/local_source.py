"""Load collector payloads from local JSON or CSV import files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_local_payload(path: Path) -> Any:
    """Load a local import file as JSON-compatible collector payload.

    Supported formats:
    - ``.json`` — either a list or an object with ``records`` / ``articles``
    - ``.csv`` — rows become ``{"records": [...]}``
    """
    if not path.exists():
        raise FileNotFoundError(f"Local import file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    if suffix == ".csv":
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return {"records": list(reader)}
    raise ValueError(f"Unsupported local import format: {path.suffix}")


def resolve_local_path(project_root: Path, configured_path: str) -> Path:
    """Resolve a configured local path relative to the project root."""
    path = Path(configured_path)
    if path.is_absolute():
        return path
    return project_root / path
