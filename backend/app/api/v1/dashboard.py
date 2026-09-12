from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.schemas.dashboard import DashboardStats
from app.services.ipam import dashboard_stats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def stats(session: AsyncSession = Depends(get_session)):
    return await dashboard_stats(session)
