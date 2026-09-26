"""Device templates (V10.1): reusable typed port layouts.

A template is data, not code — a JSONB interface list that
``POST /devices/{id}/apply-template`` / ``POST /device-templates/{id}/instantiate``
stamps onto a device in one transaction. ``interfaces`` rows look like
``{name, kind, speed_mbps?, position?, pair?}`` where ``pair`` names a
sibling entry — on apply the two get reciprocal ``pair_interface_id``
links, mirroring the generate endpoint's ``pair_prefix`` front↔back
convention. ``power_ports`` (``[{name}]``) stamps ``kind=power`` rows for
PDU outlets / PSU inlets.

``source`` is provenance: ``builtin`` rows ship with the app (seeding
writes them once per name — PATCHing a builtin flips it to ``manual``,
forking it into an editable copy of the same row), ``manual`` is
user-authored, ``import`` is reserved for future bundle restores.
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DeviceTemplate(Base):
    __tablename__ = "device_templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    manufacturer: Mapped[str | None] = mapped_column(String(255))
    model: Mapped[str | None] = mapped_column(String(255))
    # rack-library slug when one maps — the device-form prefill hook.
    device_type: Mapped[str | None] = mapped_column(String(255))
    u_height: Mapped[int] = mapped_column(default=1, server_default="1")
    face_default: Mapped[str] = mapped_column(
        String(8), default="front", server_default="front"
    )
    colour: Mapped[str | None] = mapped_column(String(7))
    category: Mapped[str | None] = mapped_column(String(64))
    watts: Mapped[int | None] = mapped_column(Integer)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    # [{name, kind, speed_mbps?, position?, pair?}] — kind must be an
    # interface_kind value; the schema layer validates on write.
    interfaces: Mapped[list] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    # [{name}] — PSU inlets / PDU outlets, stamped as kind=power ports.
    power_ports: Mapped[list | None] = mapped_column(JSONB)
    source: Mapped[str] = mapped_column(
        String(16), default="manual", server_default="manual"
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __changelog_repr__(self) -> str:
        return self.name or f"device_template#{self.id}"
