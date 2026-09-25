from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.dashboard import DashboardStats
from app.services.ipam import dashboard_stats
from app.services.review import build_review

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def stats(session: AsyncSession = Depends(get_session)):
    stats_ = await dashboard_stats(session)
    # Review queue summary for the dashboard card — sections are already
    # ordered worst-first, so the first non-empty one is the headline.
    review = await build_review(session)
    open_sections = [s for s in review["sections"] if s["count"]]
    stats_["review_open"] = sum(s["count"] for s in open_sections)
    stats_["review_worst"] = (
        open_sections[0]["title"] if open_sections else None
    )
    return stats_
