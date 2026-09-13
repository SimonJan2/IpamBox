import csv
import io
from collections.abc import Iterable

from fastapi.responses import StreamingResponse


def csv_response(filename: str, header: list[str], rows: Iterable[Iterable]) -> StreamingResponse:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    for row in rows:
        w.writerow(["" if v is None else v for v in row])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def parse_csv(text: str) -> list[dict[str, str]]:
    """CSV text -> list of row dicts (header-named, stripped)."""
    reader = csv.DictReader(io.StringIO(text))
    return [
        {k.strip().lower(): (v or "").strip() for k, v in row.items() if k}
        for row in reader
    ]
