"""V11 Reports workspace — the whole estate as one payload/workbook.

GET /reports/summary assembles every section (bounded at SECTION_ROWS);
GET /reports/export.xlsx writes one sheet per section through the bundle
exporter's workbook_response; GET /reports/{section}.csv streams the
section table through csv_response (utf-8 BOM). POST /reports/email fans
the text digest through the v7 notification channels. Nothing is
persisted — reports are derived data, no tables, no changelog.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import DATA_READ, DATA_WRITE, require_perm
from app.models.site import Site
from app.schemas.report import ReportEmailOut, ReportSummary
from app.services import reports
from app.services.csv_export import csv_response
from app.services.ipam import IPAMError, get_or_404
from app.services.rack_io import workbook_response

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(require_perm(DATA_READ))],
)


async def _scope(session: AsyncSession, site_id: int | None) -> Site | None:
    if site_id is None:
        return None
    try:
        return await get_or_404(session, Site, site_id)
    except IPAMError as e:
        raise HTTPException(e.status_code, str(e))


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _slug(site: Site | None) -> str:
    return f"-{site.slug}" if site else ""


@router.get("/summary", response_model=ReportSummary)
async def report_summary(
    site_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    site = await _scope(session, site_id)
    return await reports.build_report(session, site)


@router.get("/export.xlsx")
async def export_xlsx(
    site_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    site = await _scope(session, site_id)
    report = await reports.build_report(session, site)
    return workbook_response(
        f"ipambox-report{_slug(site)}-{_stamp()}.xlsx",
        reports.report_sheets(report),
    )


@router.post(
    "/email",
    response_model=ReportEmailOut,
    dependencies=[Depends(require_perm(DATA_WRITE))],
)
async def email_report(
    site_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    """Send the text digest to every enabled notification channel —
    summary + link, no attachment (v7 channels)."""
    site = await _scope(session, site_id)
    n = await reports.emit_report(session, site, event="report.requested")
    return ReportEmailOut(channels=n, event="report.requested")


@router.get("/{section}.csv")
async def export_section_csv(
    section: str,
    site_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    site = await _scope(session, site_id)
    report = await reports.build_report(session, site)
    sec = next(
        (s for s in report["sections"] if s["key"] == section), None
    )
    if sec is None or not sec["columns"]:
        raise HTTPException(404, f"unknown report section {section!r}")
    return csv_response(
        f"report-{section}{_slug(site)}-{_stamp()}.csv",
        sec["columns"],
        sec["rows"],
    )
