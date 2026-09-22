"""XLSX/CSV -> sheet matrices (openpyxl read_only streams / csv module)."""
import csv
import io
import zipfile
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path


@dataclass
class SheetMatrix:
    name: str
    rows: list[list] = field(default_factory=list)  # raw cell values

    @property
    def n_rows(self) -> int:
        return len([r for r in self.rows if any(v is not None and str(v).strip() for v in r)])


def _trim(rows: list[list]) -> list[list]:
    """Drop fully-empty trailing rows/cols for a stable matrix shape."""
    while rows and not any(v is not None and str(v).strip() for v in rows[-1]):
        rows.pop()
    width = max((len(r) for r in rows), default=0)
    while width and not any(
        r[width - 1] is not None and str(r[width - 1]).strip()
        for r in rows
        if len(r) >= width
    ):
        width -= 1
    return [r[:width] + [None] * (width - len(r)) for r in rows]


def _csv_sheet(payload: bytes, filename: str) -> SheetMatrix:
    """One CSV file -> one SheetMatrix named after the file stem.
    utf-8-sig first (Excel writes a BOM), cp1255 fallback for Hebrew
    exports saved as ANSI."""
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = payload.decode("cp1255")
    rows = [r for r in csv.reader(io.StringIO(text))]
    return SheetMatrix(
        name=Path(filename).stem or "sheet", rows=_trim(rows)
    )


def load_upload(payload: bytes, filename: str = "") -> list[SheetMatrix]:
    """Dispatch on container type: ZIP -> xlsx workbook; otherwise try CSV
    text (raises UnicodeDecodeError on binary garbage)."""
    if zipfile.is_zipfile(BytesIO(payload)):
        return load_workbook_bytes(payload)
    return [_csv_sheet(payload, filename)]


def load_workbook_bytes(payload: bytes) -> list[SheetMatrix]:
    """Parse workbook bytes into per-sheet row matrices.

    read_only + data_only: constant memory, evaluated formula values.
    Empty sheets come back with zero rows (classified 'empty' upstream).
    """
    import openpyxl

    wb = openpyxl.load_workbook(BytesIO(payload), read_only=True, data_only=True)
    sheets: list[SheetMatrix] = []
    try:
        for ws in wb.worksheets:
            rows = [list(row) for row in ws.iter_rows(values_only=True)]
            # trim fully-empty trailing rows/cols for a stable matrix shape
            sheets.append(SheetMatrix(name=ws.title, rows=_trim(rows)))
    finally:
        wb.close()
    return sheets
