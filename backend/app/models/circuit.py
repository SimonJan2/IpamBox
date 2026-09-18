from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Circuit(Base):
    """WAN circuit row from the קוי-SDH-IPVPN sheet (Bezeq IPVPN/SDH/Metro…).

    Legacy sheets such as קוי בזק ישן set ``is_retired`` so old circuits stay
    separate from the live inventory.
    """

    __tablename__ = "circuits"

    id: Mapped[int] = mapped_column(primary_key=True)
    env: Mapped[str | None] = mapped_column(String(64))  # סביבת חיבור (e.g. Lev)
    site_id: Mapped[int | None] = mapped_column(
        ForeignKey("sites.id", ondelete="SET NULL"), index=True
    )
    site_number: Mapped[int | None] = mapped_column(Integer)
    site_code: Mapped[str | None] = mapped_column(String(16))  # קידומת האתר
    site_name: Mapped[str | None] = mapped_column(String(255))  # מאתר
    line_type: Mapped[str | None] = mapped_column(String(32), index=True)
    bezeq_circuit_id: Mapped[str | None] = mapped_column(String(64), index=True)
    node: Mapped[str | None] = mapped_column(String(64))  # צומת
    bw_down: Mapped[str | None] = mapped_column(String(32))  # "500", "1G"
    bw_up: Mapped[str | None] = mapped_column(String(32))
    wan_ip: Mapped[str | None] = mapped_column(INET)  # כתובת WAN
    app_client_num: Mapped[str | None] = mapped_column(String(64))
    app_client_name: Mapped[str | None] = mapped_column(String(255))
    app_service_type: Mapped[str | None] = mapped_column(String(255))
    contact: Mapped[str | None] = mapped_column(Text)  # איש קשר וכתובת האתר
    status: Mapped[str | None] = mapped_column(String(64))  # raw Hebrew status
    notes: Mapped[str | None] = mapped_column(Text)
    # True for rows imported from legacy sheets (e.g. קוי בזק ישן)
    is_retired: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", index=True
    )
    import_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("import_batches.id", ondelete="SET NULL"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    site: Mapped["Site | None"] = relationship()  # noqa: F821

    def __changelog_repr__(self) -> str:
        return self.bezeq_circuit_id or f"circuit#{self.id}"
