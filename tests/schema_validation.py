"""Shared JSON Schema validation for API contract tests (Phase 15).

Schemas live in ``tests/schemas/`` as byte-identical copies of
``postman/schemas/``. Same-directory ``{"$ref": "<file>"}`` references are
resolved locally before validation. Failures list every violation as
``<path>: <message>`` so the missing property, wrong type, or broken
structure is immediately visible.
"""

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

SCHEMA_DIRECTORY = Path(__file__).parent / "schemas"


def _resolve_local_refs(node: Any, base_dir: Path) -> Any:
    if isinstance(node, dict):
        if set(node) == {"$ref"} and isinstance(node["$ref"], str):
            ref_file = (base_dir / node["$ref"]).resolve()
            assert ref_file.parent == base_dir.resolve(), (
                f"ref escapes schemas dir: {node['$ref']}"
            )
            return _resolve_local_refs(
                json.loads(ref_file.read_text(encoding="utf-8")), base_dir
            )
        return {k: _resolve_local_refs(v, base_dir) for k, v in node.items()}
    if isinstance(node, list):
        return [_resolve_local_refs(v, base_dir) for v in node]
    return node


def validate_schema(instance: Any, schema_name: str) -> None:
    """Validate an API response instance against a checked-in Draft 7 schema."""
    schema = _resolve_local_refs(
        json.loads((SCHEMA_DIRECTORY / schema_name).read_text(encoding="utf-8")),
        SCHEMA_DIRECTORY,
    )
    Draft7Validator.check_schema(schema)
    errors = sorted(
        Draft7Validator(schema).iter_errors(instance),
        key=lambda e: list(e.path),
    )
    assert not errors, (
        f"response violates {schema_name}:\n"
        + "\n".join(
            f"  {'/'.join(str(p) for p in e.absolute_path) or '(root)'}: {e.message}"
            for e in errors
        )
    )
