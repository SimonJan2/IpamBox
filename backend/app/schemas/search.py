from datetime import date

from pydantic import BaseModel


class SearchAddress(BaseModel):
    id: int
    address: str
    hostname: str | None
    prefix_id: int
    status: str


class SearchPrefix(BaseModel):
    id: int
    prefix: str
    description: str | None
    vrf_id: int
    site_id: int | None


class SearchSite(BaseModel):
    id: int
    name: str
    code: str | None
    site_number: int | None


class SearchVrf(BaseModel):
    id: int
    name: str
    rd: str | None
    site_id: int | None


class SearchVlan(BaseModel):
    id: int
    vid: int
    name: str


class SearchCircuit(BaseModel):
    id: int
    site_name: str | None
    site_code: str | None
    bezeq_circuit_id: str | None
    line_type: str | None
    app_client_name: str | None


class SearchCertificate(BaseModel):
    id: int
    cert_name: str | None
    server_name: str | None
    platform: str | None
    expires_on: date | None


class SearchAsset(BaseModel):
    id: int
    kind: str
    vendor: str | None
    model: str | None
    serial_number: str | None
    category: str | None


class SearchService(BaseModel):
    id: int
    name: str | None
    beneficiary: str | None
    site_code: str | None


class SearchList(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None


class SearchListRow(BaseModel):
    id: int
    list_id: int
    list_slug: str
    list_name: str
    label: str


class SearchJump(BaseModel):
    """q parsed as an IP address -> the deepest prefix containing it."""
    address: str
    prefix_id: int
    prefix: str
    exists: bool


class SearchOut(BaseModel):
    addresses: list[SearchAddress]
    prefixes: list[SearchPrefix]
    sites: list[SearchSite]
    vrfs: list[SearchVrf]
    vlans: list[SearchVlan]
    circuits: list[SearchCircuit]
    certificates: list[SearchCertificate]
    assets: list[SearchAsset]
    services: list[SearchService]
    lists: list[SearchList] = []
    list_rows: list[SearchListRow] = []
    jump: SearchJump | None
