"use client";

/**
 * TopologyMap — the device-adjacency canvas (V10).
 *
 * One React Flow canvas fed by /topology/graph: devices (and optionally
 * unlinked IP hosts) are nodes, documented cables collapse into edges.
 * Layout is elkjs layered with compound nodes — site → rack group → rack,
 * unracked devices in a "No rack" lane, unlinked hosts in a dimmed outer
 * lane. elk runs fully client-side (bundled build — no worker, no CDN).
 *
 * Read-only lens: nodes aren't connectable/deletable; dragging is allowed
 * but only persists when the owner presses "Save layout".
 */
import ELK from "elkjs/lib/elk.bundled.js";
import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
  type NodeTypes,
  type OnEdgesChange,
  type OnNodesChange,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { cn } from "@/lib/utils";
import { STATUS_TOKENS } from "@/lib/status-tokens";
import type {
  TopoHealth,
  TopologyEdge,
  TopologyGraph,
  TopologyNode as TopoNodeData,
} from "@/types";

export const NODE_W = 200;
export const NODE_H = 54;

// --- node data -------------------------------------------------------------

export interface DeviceNodeData extends Record<string, unknown> {
  node: TopoNodeData;
  overlay: boolean;
}
export interface IpNodeData extends Record<string, unknown> {
  node: TopoNodeData;
  overlay: boolean;
}
export interface GroupNodeData extends Record<string, unknown> {
  label: string;
  variant: "site" | "group" | "rack" | "lane" | "unlinked";
}

export type TopoNode = Node<DeviceNodeData | IpNodeData | GroupNodeData>;

// RF's Edge.data wants a Record — nest the graph payload under `edge`
// rather than weakening TopologyEdge with an index signature.
export interface TopoEdgeData extends Record<string, unknown> {
  edge: TopologyEdge;
}
export type TopoEdge = Edge<TopoEdgeData>;

// --- elk layout ------------------------------------------------------------

const elk = new ELK();

const ELK_OPTIONS = {
  "elk.algorithm": "layered",
  "elk.direction": "RIGHT",
  "elk.hierarchyHandling": "INCLUDE_CHILDREN",
  "elk.padding": "[top=44,left=18,bottom=18,right=18]",
  "elk.spacing.nodeNode": "22",
  "elk.layered.spacing.nodeNodeBetweenLayers": "64",
  "elk.spacing.componentComponent": "48",
  "elk.layered.spacing.edgeNodeBetweenLayers": "20",
  // Cross-hierarchy edges (device in rack A → device in rack B) are the
  // whole point — let elk consider them when ordering layers.
  "elk.layered.crossHierarchyEdgeStraightness": "true",
};

interface ElkChild {
  id: string;
  width?: number;
  height?: number;
  children?: ElkChild[];
  labels?: { text: string }[];
}

/**
 * Build the compound tree: site → rack group → rack, "No rack" lanes for
 * unracked devices, "No site" + "Unlinked hosts" outer lanes. Only groups
 * that actually hold nodes are emitted.
 */
function buildTree(graph: TopologyGraph): ElkChild[] {
  const devNodes = graph.nodes.filter((n) => n.kind === "device");
  const ipNodes = graph.nodes.filter((n) => n.kind === "ip");

  const siteById = new Map(graph.groups.sites.map((s) => [s.id, s]));
  const groupById = new Map(graph.groups.rack_groups.map((g) => [g.id, g]));
  const rackById = new Map(graph.groups.racks.map((r) => [r.id, r]));

  const leaf = (n: TopoNodeData): ElkChild => ({
    id: n.id,
    width: NODE_W,
    height: NODE_H,
  });

  const labelFor = (id: string): string => {
    if (id === "nosite") return "No site";
    if (id === "unlinked") return "Unlinked hosts";
    if (id.startsWith("norack-")) return "No rack";
    if (id.startsWith("site-"))
      return siteById.get(Number(id.slice(5)))?.name ?? "Site";
    if (id.startsWith("group-"))
      return groupById.get(Number(id.slice(6)))?.name ?? "Row";
    if (id.startsWith("rack-"))
      return rackById.get(Number(id.slice(5)))?.name ?? "Rack";
    return id;
  };

  /** Immediate parent group id, or null for a top-level lane. Pure
   *  function of the id — ancestors are computed by closing over it. */
  const parentOf = (id: string): string | null => {
    if (id === "nosite" || id === "unlinked" || id.startsWith("site-"))
      return null;
    if (id.startsWith("norack-")) return id.slice(7); // norack-site-3 → site-3
    if (id.startsWith("group-")) {
      const g = groupById.get(Number(id.slice(6)));
      return g?.site_id != null ? `site-${g.site_id}` : "nosite";
    }
    if (id.startsWith("rack-")) {
      const r = rackById.get(Number(id.slice(5)));
      return r?.group_id != null && groupById.has(r.group_id)
        ? `group-${r.group_id}`
        : r?.site_id != null
          ? `site-${r.site_id}`
          : "nosite";
    }
    return null;
  };

  // Pass 1 — leaves into their immediate parent group.
  const groups = new Map<string, ElkChild>();
  const grp = (id: string): ElkChild => {
    let g = groups.get(id);
    if (!g) {
      g = { id, labels: [{ text: labelFor(id) }], children: [] };
      groups.set(id, g);
    }
    return g;
  };

  for (const d of devNodes) {
    const rack = d.rack_id != null ? rackById.get(d.rack_id) : undefined;
    if (rack) {
      grp(`rack-${rack.id}`).children!.push(leaf(d));
      continue;
    }
    grp(
      `norack-${d.site_id != null ? `site-${d.site_id}` : "nosite"}`
    ).children!.push(leaf(d));
  }
  for (const n of ipNodes) grp("unlinked").children!.push(leaf(n));

  // Pass 2 — every group gets wired upward; missing ancestors are created
  // through the parentOf closure so a site exists even when only a rack
  // in it is visible.
  const allIds = new Set<string>();
  for (const id of groups.keys()) {
    let cur: string | null = id;
    while (cur && !allIds.has(cur)) {
      allIds.add(cur);
      cur = parentOf(cur);
    }
  }
  const roots: ElkChild[] = [];
  // Sorted for a deterministic sibling order — elk output then doesn't
  // depend on Map/Set iteration order.
  for (const id of [...allIds].sort()) {
    const pid = parentOf(id);
    if (pid === null) roots.push(grp(id));
    else grp(pid).children!.push(grp(id));
  }
  // Deterministic order: named sites first, then No site, unlinked last.
  const order = (id: string) =>
    id === "unlinked" ? 2 : id === "nosite" ? 1 : 0;
  roots.sort((a, b) => order(a.id) - order(b.id));
  return roots;
}

/** walk the laid-out elk tree -> RF nodes (parents before children) +
 *  RF edges, with saved positions overriding elk where they exist. */
export async function layoutGraph(
  graph: TopologyGraph,
  saved: Record<string, { x: number; y: number }>,
  overlay: boolean
): Promise<{ nodes: TopoNode[]; edges: TopoEdge[] }> {
  const children = buildTree(graph);
  const laidOut = await elk.layout({
    id: "root",
    layoutOptions: ELK_OPTIONS,
    children,
    edges: graph.edges.map((e, i) => ({
      id: `e-${i}`,
      sources: [e.a],
      targets: [e.b],
    })),
  });

  const rawById = new Map(graph.nodes.map((n) => [n.id, n]));
  const groupLabel = new Map<string, string>();
  for (const g of graph.groups.sites) groupLabel.set(`site-${g.id}`, g.name);
  for (const g of graph.groups.rack_groups)
    groupLabel.set(`group-${g.id}`, g.name);
  for (const r of graph.groups.racks) groupLabel.set(`rack-${r.id}`, r.name);

  const variantOf = (id: string): GroupNodeData["variant"] =>
    id === "unlinked"
      ? "unlinked"
      : id.startsWith("norack-") || id === "nosite"
        ? "lane"
        : id.startsWith("site-")
          ? "site"
          : id.startsWith("group-")
            ? "group"
            : "rack";

  const nodes: TopoNode[] = [];
  const walk = (c: ElkChild & { x?: number; y?: number }, parent?: string) => {
    const pos = { x: c.x ?? 0, y: c.y ?? 0 };
    const savedPos = saved[c.id];
    const leaf = rawById.get(c.id);
    if (leaf) {
      nodes.push({
        id: c.id,
        type: leaf.kind === "ip" ? "topoIp" : "topoDevice",
        position: savedPos ?? pos,
        parentId: parent,
        data: { node: leaf, overlay },
        width: NODE_W,
        height: NODE_H,
        draggable: true,
        selectable: true,
        connectable: false,
        deletable: false,
      });
    } else {
      nodes.push({
        id: c.id,
        type: "topoGroup",
        position: savedPos ?? pos,
        parentId: parent,
        data: {
          label:
            groupLabel.get(c.id) ??
            (c.labels?.[0]?.text || c.id),
          variant: variantOf(c.id),
        },
        style: { width: c.width, height: c.height },
        draggable: true,
        selectable: false,
        connectable: false,
        deletable: false,
      });
      for (const kid of (c.children ?? []) as ElkChild[]) walk(kid, c.id);
    }
  };
  for (const c of (laidOut.children ?? []) as ElkChild[]) walk(c);

  const edges: TopoEdge[] = graph.edges.map((e, i) => ({
    id: `e-${i}`,
    source: e.a,
    target: e.b,
    label:
      e.mismatched || e.count > 1
        ? `${e.mismatched ? "⚠ " : ""}${e.count > 1 ? `×${e.count}` : ""}`.trim()
        : undefined,
    labelStyle: e.mismatched ? { fill: "hsl(var(--destructive))" } : undefined,
    labelBgStyle: e.mismatched
      ? { fill: "hsl(var(--destructive) / 0.12)" }
      : undefined,
    style: e.mismatched
      ? { stroke: "hsl(var(--destructive))", strokeWidth: 1.8 }
      : undefined,
    className: "topo-edge",
    data: { edge: e },
  }));
  return { nodes, edges };
}

// --- node renderers ---------------------------------------------------------

function HealthDot({ health }: { health: TopoHealth }) {
  const dot =
    health === "unmonitored"
      ? "bg-transparent border border-muted-foreground/60"
      : STATUS_TOKENS[health].dot;
  return (
    <span
      className={cn("mt-0.5 h-2.5 w-2.5 shrink-0 rounded-full", dot)}
      title={health}
      aria-label={`health: ${health}`}
    />
  );
}

function DeviceNode({ data }: NodeProps) {
  const d = data as DeviceNodeData;
  const n = d.node;
  return (
    <div className="flex h-full w-full items-center gap-2 rounded-md border bg-card px-2.5 py-1.5 shadow-sm">
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={false}
        className="!bg-transparent !border-0"
      />
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={false}
        className="!bg-transparent !border-0"
      />
      {d.overlay && <HealthDot health={n.health} />}
      <div className="min-w-0 flex-1">
        <div className="truncate text-[13px] font-medium leading-tight">
          {n.label}
        </div>
        <div className="truncate text-[10px] text-muted-foreground">
          {[n.device_type, n.cabled_count != null && n.interface_count != null
            ? `${n.cabled_count}/${n.interface_count} ports`
            : null]
            .filter(Boolean)
            .join(" · ") || "device"}
        </div>
      </div>
    </div>
  );
}

function IpNode({ data }: NodeProps) {
  const d = data as IpNodeData;
  const n = d.node;
  return (
    <div className="flex h-full w-full items-center gap-2 rounded-md border border-dashed bg-card/60 px-2.5 py-1.5">
      <Handle
        type="target"
        position={Position.Left}
        isConnectable={false}
        className="!bg-transparent !border-0"
      />
      <Handle
        type="source"
        position={Position.Right}
        isConnectable={false}
        className="!bg-transparent !border-0"
      />
      {d.overlay && <HealthDot health={n.health} />}
      <div className="min-w-0 flex-1">
        <div className="truncate text-[13px] leading-tight text-muted-foreground">
          {n.label}
        </div>
        <div className="truncate text-[10px] text-muted-foreground/70">
          unlinked host
        </div>
      </div>
    </div>
  );
}

const GROUP_STYLE: Record<GroupNodeData["variant"], string> = {
  site: "border-foreground/15 bg-accent/20",
  group: "border-foreground/10 bg-accent/10",
  rack: "border-border bg-card/40",
  lane: "border-dashed border-border bg-transparent",
  unlinked: "border-dashed border-border bg-muted/30 opacity-75",
};

function GroupNode({ data }: NodeProps) {
  const d = data as GroupNodeData;
  return (
    <div
      className={cn("h-full w-full rounded-lg border", GROUP_STYLE[d.variant])}
    >
      <div
        className={cn(
          "px-2 pt-1.5 text-[11px] font-semibold uppercase tracking-wider",
          d.variant === "unlinked" || d.variant === "lane"
            ? "text-muted-foreground/70"
            : "text-muted-foreground"
        )}
      >
        {d.label}
      </div>
    </div>
  );
}

const nodeTypes: NodeTypes = {
  topoDevice: DeviceNode,
  topoIp: IpNode,
  topoGroup: GroupNode,
};

// --- the canvas -------------------------------------------------------------

export interface TopologyMapProps {
  nodes: TopoNode[];
  edges: TopoEdge[];
  onNodesChange: OnNodesChange<TopoNode>;
  onEdgesChange: OnEdgesChange<TopoEdge>;
  onNodeClick?: (node: TopoNode) => void;
  onNodeDoubleClick?: (node: TopoNode) => void;
  onEdgeClick?: (edge: TopoEdge, at: { x: number; y: number }) => void;
  onPaneClick?: () => void;
  onNodeDragStop?: () => void;
}

export function TopologyMap({
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onNodeClick,
  onNodeDoubleClick,
  onEdgeClick,
  onPaneClick,
  onNodeDragStop,
}: TopologyMapProps) {
  return (
    <ReactFlow<TopoNode, TopoEdge>
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={(_, n) => onNodeClick?.(n)}
      onNodeDoubleClick={(_, n) => onNodeDoubleClick?.(n)}
      onEdgeClick={(e, edge) =>
        onEdgeClick?.(edge, { x: e.clientX, y: e.clientY })
      }
      onPaneClick={onPaneClick}
      onNodeDragStop={onNodeDragStop}
      fitView
      fitViewOptions={{ padding: 0.15, maxZoom: 1.2 }}
      minZoom={0.1}
      onlyRenderVisibleElements
      nodesConnectable={false}
      deleteKeyCode={null}
      proOptions={{ hideAttribution: false }}
      className="topo-canvas"
    >
      <Background gap={24} />
      <Controls showInteractive={false} />
      <MiniMap pannable zoomable className="!bg-card" />
    </ReactFlow>
  );
}
