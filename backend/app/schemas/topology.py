"""Topology map schemas (V10) — the /topology/graph aggregate payload and
the diagram_layouts round-trip.

The graph is derived data: nodes are devices (+ optional unlinked IPs),
edges are *documented cables* collapsed device↔device — the map draws
measured adjacency, not hierarchy-as-diagram. Patch-panel chains are NOT
resolved through panels here: an edge means "a cable directly joins
these two devices" (the L1 trace view already owns hop-through
semantics).
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

NodeKind = Literal["device", "ip"]


class TopologyNode(BaseModel):
    """One canvas node. `id` is a namespaced string ("dev-12",
    "unlinked-55") so devices and IP-only hosts share one id space."""

    id: str
    kind: NodeKind
    label: str
    # IPStatus value, or "unmonitored" when a device links no IPs (the
    # HEALTH_CLASSES vocabulary — the frontend colors by this verbatim).
    health: str
    # Effective site: explicit device.site_id wins, racked devices inherit
    # their rack's site. Unlinked IPs take their prefix's site.
    site_id: int | None = None
    rack_id: int | None = None
    rack_group_id: int | None = None
    device_type: str | None = None
    # Port coverage for the side panel (device kind only).
    interface_count: int | None = None
    cabled_count: int | None = None
    # IP-only extras (kind == "ip").
    hostname: str | None = None
    prefix_id: int | None = None
    href: str


class TopologyEdgeCable(BaseModel):
    """One member cable of a collapsed edge — feeds the edge popover."""

    id: int
    kind: str
    label: str | None = None
    a_label: str  # "device · port"
    b_label: str
    # Raw ids for popover links (/devices/{id}, ?trace={interface_id}).
    a_device_id: int
    b_device_id: int
    a_interface_id: int
    b_interface_id: int


class TopologyEdge(BaseModel):
    """All cables between the same device pair collapse into one edge."""

    a: str
    b: str
    count: int
    kinds: list[str]
    # v8.2: true when any member interface carries validation.cable_mismatch.
    mismatched: bool
    cables: list[TopologyEdgeCable]


class TopologySiteRef(BaseModel):
    id: int
    name: str


class TopologyRackGroupRef(BaseModel):
    id: int
    name: str
    site_id: int | None


class TopologyRackRef(BaseModel):
    id: int
    name: str
    site_id: int | None
    group_id: int | None


class TopologyGroups(BaseModel):
    """Compound-node vocabulary for the canvas: site → rack group → rack."""

    sites: list[TopologySiteRef]
    rack_groups: list[TopologyRackGroupRef]
    racks: list[TopologyRackRef]


class TopologyGraph(BaseModel):
    nodes: list[TopologyNode]
    edges: list[TopologyEdge]
    groups: TopologyGroups


class NodePosition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float


class DiagramLayoutOut(BaseModel):
    key: str
    # {node_id: {x, y}} — canvas positions relative to each node's parent.
    positions: dict[str, NodePosition]
    updated_at: datetime | None = None


class DiagramLayoutPut(BaseModel):
    key: str = Field(default="main", min_length=1, max_length=64)
    positions: dict[str, NodePosition] = Field(default_factory=dict)
