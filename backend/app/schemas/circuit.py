from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import ip_display


class CircuitCreate(BaseModel):
    env: str | None = Field(default=None, max_length=64)
    site_id: int | None = None
    site_number: int | None = None
    site_code: str | None = Field(default=None, max_length=16)
    site_name: str | None = Field(default=None, max_length=255)
    line_type: str | None = Field(default=None, max_length=32)
    bezeq_circuit_id: str | None = Field(default=None, max_length=64)
    node: str | None = Field(default=None, max_length=64)
    bw_down: str | None = Field(default=None, max_length=32)
    bw_up: str | None = Field(default=None, max_length=32)
    wan_ip: str | None = None
    app_client_num: str | None = Field(default=None, max_length=64)
    app_client_name: str | None = Field(default=None, max_length=255)
    app_service_type: str | None = Field(default=None, max_length=255)
    contact: str | None = None
    status: str | None = Field(default=None, max_length=64)
    notes: str | None = None
    is_retired: bool = False

    @field_validator("wan_ip")
    @classmethod
    def _wan(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        import ipaddress

        try:
            return str(ipaddress.ip_address(v.strip()))
        except ValueError as exc:
            raise ValueError(f"invalid WAN IP: {v}") from exc


class CircuitUpdate(BaseModel):
    env: str | None = Field(default=None, max_length=64)
    site_id: int | None = None
    site_number: int | None = None
    site_code: str | None = Field(default=None, max_length=16)
    site_name: str | None = Field(default=None, max_length=255)
    line_type: str | None = Field(default=None, max_length=32)
    bezeq_circuit_id: str | None = Field(default=None, max_length=64)
    node: str | None = Field(default=None, max_length=64)
    bw_down: str | None = Field(default=None, max_length=32)
    bw_up: str | None = Field(default=None, max_length=32)
    wan_ip: str | None = None
    app_client_num: str | None = Field(default=None, max_length=64)
    app_client_name: str | None = Field(default=None, max_length=255)
    app_service_type: str | None = Field(default=None, max_length=255)
    contact: str | None = None
    status: str | None = Field(default=None, max_length=64)
    notes: str | None = None
    is_retired: bool = False

    @field_validator("wan_ip")
    @classmethod
    def _wan(cls, v: str | None) -> str | None:
        return CircuitCreate._wan(v)


class CircuitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    env: str | None
    site_id: int | None
    site_number: int | None
    site_code: str | None
    site_name: str | None
    line_type: str | None
    bezeq_circuit_id: str | None
    node: str | None
    bw_down: str | None
    bw_up: str | None
    wan_ip: str | None
    app_client_num: str | None
    app_client_name: str | None
    app_service_type: str | None
    contact: str | None
    status: str | None
    notes: str | None
    is_retired: bool
    import_batch_id: int | None
    created_at: datetime

    @field_validator("wan_ip", mode="before")
    @classmethod
    def _wan_str(cls, v):
        return ip_display(v)
