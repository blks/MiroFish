"""
Coerce LLM-shaped ontology attribute entries into dicts with a ``name`` field.

Models sometimes return ``attributes`` as a list of strings instead of objects.
"""

from __future__ import annotations

import re
from typing import Any, Optional


def python_safe_field_name(raw: str, index: int) -> str:
    """Valid Python identifier for dynamic Pydantic / Zep model fields."""
    s = re.sub(r"\s+", "_", str(raw).strip())
    s = re.sub(r"[^0-9a-zA-Z_]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_") or f"attr_{index}"
    if s and s[0].isdigit():
        s = f"attr_{s}"
    return s


def coerce_ontology_attribute_def(attr_def: Any, index: int) -> Optional[dict[str, Any]]:
    if isinstance(attr_def, str):
        raw = attr_def.strip()
        if not raw:
            return None
        return {"name": raw, "type": "text", "description": ""}
    if not isinstance(attr_def, dict):
        return None
    name = attr_def.get("name")
    if name is not None and str(name).strip():
        return attr_def
    for alt in ("field", "key", "attr_name", "attribute"):
        v = attr_def.get(alt)
        if v is not None and str(v).strip():
            merged = dict(attr_def)
            merged["name"] = str(v).strip()
            return merged
    return None
