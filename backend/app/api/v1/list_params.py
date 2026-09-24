"""List-endpoint filter param parsing — the URL vocabulary.

Facets are multi-select in the UI, so these params accept comma-separated
sets (the `status`/`tags` precedent on /addresses): `site_id=1,2` is a set,
a bare `site_id=1` is a set of one. Bad values 422 rather than silently
filtering wrong — a typo'd view should fail loudly.
"""
from enum import Enum
from typing import Iterable, TypeVar

from fastapi import HTTPException

E = TypeVar("E", bound=Enum)


def parse_int_set(raw: str | None, name: str) -> set[int] | None:
    """CSV of ints -> set; None when absent/blank, 422 on non-numeric."""
    if raw is None or not raw.strip():
        return None
    try:
        return {int(p.strip()) for p in raw.split(",") if p.strip()}
    except ValueError:
        raise HTTPException(422, f"bad {name} value: {raw!r}")


def parse_enum_set(
    raw: str | None, name: str, enum: type[E]
) -> set[E] | None:
    """CSV of enum values -> set; 422 on an unknown value."""
    if raw is None or not raw.strip():
        return None
    try:
        return {enum(p.strip()) for p in raw.split(",") if p.strip()}
    except ValueError as e:
        raise HTTPException(422, f"bad {name} value: {e}")


def parse_token_set(
    raw: str | None, name: str, allowed: Iterable[str]
) -> set[str] | None:
    """CSV of literal tokens -> set; 422 on a value outside `allowed`."""
    if raw is None or not raw.strip():
        return None
    vals = {p.strip() for p in raw.split(",") if p.strip()}
    bad = vals - set(allowed)
    if bad:
        raise HTTPException(422, f"bad {name} value: {sorted(bad)[0]!r}")
    return vals


def parse_str_set(raw: str | None) -> set[str] | None:
    """CSV of free-form exact-match strings -> set. No fixed vocabulary —
    used for open-ended columns like `source` (manual/rackula/import/…)."""
    if raw is None or not raw.strip():
        return None
    return {p.strip() for p in raw.split(",") if p.strip()}
