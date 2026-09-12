import json
import re
from functools import lru_cache
from pathlib import Path

_DATA = Path(__file__).resolve().parent.parent / "data" / "oui.json"


@lru_cache(maxsize=1)
def _table() -> dict[str, str]:
    if not _DATA.exists():
        return {}
    return json.loads(_DATA.read_text())


def vendor_for(mac: str | None) -> str | None:
    """Longest-prefix OUI lookup (handles MA-L/MA-M/MA-S blocks)."""
    if not mac:
        return None
    hexs = re.sub(r"[^0-9A-Fa-f]", "", mac).upper()
    if len(hexs) < 6:
        return None
    table = _table()
    for n in (9, 7, 6):  # /36, /28, /24
        if len(hexs) >= n and hexs[:n] in table:
            return table[hexs[:n]]
    return None
