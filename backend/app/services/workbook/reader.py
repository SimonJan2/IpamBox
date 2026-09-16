"""XLSX -> sheet matrices via openpyxl (read_only streams, values only)."""
from dataclasses import dataclass, field
from io import BytesIO


@dataclass
class SheetMatrix:
    name: str
    rows: list[list] = field(default_factory=list)  # raw cell values

    @property
    def n_rows(self) -> int:
        return len([r for r in self.rows if any(v is not None and str(v).strip() for v in r)])


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
            while rows and not any(v is not None and str(v).strip() for v in rows[-1]):
                rows.pop()
            width = max((len(r) for r in rows), default=0)
            while width and not any(
                r[width - 1] is not None and str(r[width - 1]).strip()
                for r in rows
                if len(r) >= width
            ):
                width -= 1
            sheets.append(
                SheetMatrix(name=ws.title, rows=[r[:width] + [None] * (width - len(r)) for r in rows])
            )
    finally:
        wb.close()
    return sheets
