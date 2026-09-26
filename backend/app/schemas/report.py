"""V11 Reports workspace — one payload drives page, CSVs and workbook.

Sections are deliberately generic (columns + rows) so the same contract
feeds the summary cards, the per-section CSV endpoint and the
multi-sheet XLSX export without per-section response models."""
from typing import Any

from pydantic import BaseModel


class ReportMetric(BaseModel):
    label: str
    value: int | float | str | None


class ReportSection(BaseModel):
    key: str
    title: str
    href: str | None = None
    note: str | None = None
    metrics: list[ReportMetric] = []
    columns: list[str] = []
    rows: list[list[Any]] = []
    total_rows: int = 0
    truncated: bool = False


class ReportSite(BaseModel):
    id: int
    name: str
    slug: str | None = None


class ReportSummary(BaseModel):
    generated_at: str
    site: ReportSite | None = None
    metrics: list[ReportMetric] = []
    sections: list[ReportSection] = []


class ReportEmailOut(BaseModel):
    """Ack for POST /reports/email — deliveries attempted."""
    channels: int
    event: str
