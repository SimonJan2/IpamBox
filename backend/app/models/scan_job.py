import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ScanStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    arq_job_id: Mapped[str | None] = mapped_column(String(64))
    cidr: Mapped[str] = mapped_column(String(64))
    vrf_id: Mapped[int | None] = mapped_column(ForeignKey("vrfs.id", ondelete="SET NULL"), index=True)
    prefix_id: Mapped[int | None] = mapped_column(ForeignKey("prefixes.id", ondelete="SET NULL"), index=True)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(
            ScanStatus,
            name="scan_status",
            native_enum=True,
            values_callable=lambda e: [m.value for m in e],
        ),
        default=ScanStatus.QUEUED,
        server_default=ScanStatus.QUEUED.value,
        index=True,
    )
    progress: Mapped[float] = mapped_column(Float, default=0.0, server_default="0")
    total_hosts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    hosts_discovered: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    hosts_new: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    error: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), )
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    vrf: Mapped["VRF | None"] = relationship()  # noqa: F821
    prefix: Mapped["Prefix | None"] = relationship()  # noqa: F821
