"use client";

/**
 * /topology — the device-adjacency canvas (V10).
 *
 * Fetches the whole graph payload plus the saved "main" layout, lays the
 * nodes out with elk, then overlays saved positions for ids the layout
 * knows. Dragging is allowed; positions persist only via "Save layout"
 * (data:write). "Auto-layout" reverts the canvas to pure elk.
 */
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  LayoutGrid,
  Loader2,
  Save,
  Share2,
  X,
} from "lucide-react";
import { useEdgesState, useNodesState } from "@xyflow/react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { usePrefs } from "@/lib/prefs";
import { useUrlParam } from "@/lib/url-state";
import type { TopologyGraph, TopologyLayout, TopologyNode } from "@/types";
import {
  layoutGraph,
  TopologyMap,
  type TopoEdge,
  type TopoNode,
} from "@/components/topology-map";
import { DocsLink } from "@/components/docs/docs-link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface EdgePopup {
  edge: TopoEdge;
  x: number;
  y: number;
}

export default function TopologyClient() {
  const router = useRouter();
  const { can } = useAuth();
  const [prefs, setPrefs] = usePrefs();
  const overlay = prefs.topoHealth;

  const [site, setSite] = useUrlParam("site", "all");
  // Unlinked hosts default OFF — on real data they can outnumber devices
  // 40:1 and bury the canvas; `unlinked=1` in the URL opts in.
  const [unlinked, setUnlinked] = useUrlParam("unlinked", "0");

  const [graph, setGraph] = useState<TopologyGraph | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState<TopoNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<TopoEdge>([]);
  const [layoutNonce, setLayoutNonce] = useState(0); // bump → refit
  const [busy, setBusy] = useState(false);
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [selected, setSelected] = useState<TopologyNode | null>(null);
  const [popup, setPopup] = useState<EdgePopup | null>(null);

  // Positions as last persisted — merges into the PUT so nodes hidden by
  // a site filter keep their saved spot.
  const savedRef = useRef<Record<string, { x: number; y: number }>>({});

  const load = useCallback(() => {
    setError(null);
    setBusy(true);
    const gq = new URLSearchParams({ include_unlinked: unlinked });
    if (site !== "all") gq.set("site_id", site);
    Promise.all([
      api.get<TopologyGraph>(`/api/v1/topology/graph?${gq}`),
      api.get<TopologyLayout>("/api/v1/topology/layout?key=main"),
    ])
      .then(async ([g, lay]) => {
        savedRef.current = lay.positions;
        const laid = await layoutGraph(g, lay.positions, overlay);
        setGraph(g);
        setNodes(laid.nodes);
        setEdges(laid.edges);
        setDirty(false);
        setLayoutNonce((n) => n + 1);
      })
      .catch((e) => {
        setError(String(e));
        toast.error("Failed to load topology", { description: String(e) });
      })
      .finally(() => setBusy(false));
    // overlay is applied to node data post-layout, never triggers reload
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [site, unlinked]);
  useEffect(load, [load]);

  // Health overlay toggle: patch node data in place — no relayout.
  useEffect(() => {
    setNodes((ns) =>
      ns.map((n) =>
        n.type === "topoDevice" || n.type === "topoIp"
          ? { ...n, data: { ...n.data, overlay } }
          : n
      )
    );
  }, [overlay, setNodes]);

  const siteName = useCallback(
    (id: number | null) =>
      graph?.groups.sites.find((s) => s.id === id)?.name ?? null,
    [graph]
  );
  const rackName = useCallback(
    (id: number | null) =>
      graph?.groups.racks.find((r) => r.id === id)?.name ?? null,
    [graph]
  );

  const save = async () => {
    setSaving(true);
    try {
      const cur: Record<string, { x: number; y: number }> = {};
      for (const n of nodes) cur[n.id] = { x: n.position.x, y: n.position.y };
      const positions = { ...savedRef.current, ...cur };
      const r = await api.put<TopologyLayout>("/api/v1/topology/layout", {
        key: "main",
        positions,
      });
      savedRef.current = r.positions;
      setDirty(false);
      toast.success("Layout saved");
    } catch (e) {
      toast.error("Couldn't save layout", { description: String(e) });
    } finally {
      setSaving(false);
    }
  };

  const autoLayout = async () => {
    if (!graph) return;
    setBusy(true);
    try {
      // Pure elk — saved positions and drags both reset.
      const laid = await layoutGraph(graph, {}, overlay);
      setNodes(laid.nodes);
      setEdges(laid.edges);
      setDirty(true);
      setLayoutNonce((n) => n + 1);
    } finally {
      setBusy(false);
    }
  };

  const onNodeClick = (n: TopoNode) => {
    if (n.type === "topoGroup") return;
    setPopup(null);
    setSelected((n.data as { node: TopologyNode }).node);
  };
  const onNodeDoubleClick = (n: TopoNode) => {
    if (n.type === "topoGroup") return;
    router.push((n.data as { node: TopologyNode }).node.href);
  };

  const stats = useMemo(() => {
    const devs = graph?.nodes.filter((n) => n.kind === "device").length ?? 0;
    const ips = graph?.nodes.filter((n) => n.kind === "ip").length ?? 0;
    return { devs, ips, edges: graph?.edges.length ?? 0 };
  }, [graph]);

  return (
    <div className="flex h-[calc(100dvh-8rem)] flex-col gap-4">
      <div className="flex items-center justify-between">
        <h1 className="flex items-center gap-2 text-xl font-semibold">
          <Share2 className="h-5 w-5 text-emerald-400" /> Topology
          {graph && (
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              {stats.devs} devices · {stats.edges} links
              {stats.ips > 0 ? ` · ${stats.ips} unlinked` : ""}
            </span>
          )}
          <DocsLink slug="topology" />
        </h1>
        <div className="flex items-center gap-2">
          {can(PERM.DATA_WRITE) && (
            <Button
              size="sm"
              variant="outline"
              onClick={save}
              disabled={!dirty || saving}
              title="Persist the current arrangement as the shared layout"
            >
              {saving ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              Save layout
              {dirty && (
                <span
                  className="h-1.5 w-1.5 rounded-full bg-amber-400"
                  aria-label="unsaved changes"
                />
              )}
            </Button>
          )}
          <Button
            size="sm"
            variant="outline"
            onClick={autoLayout}
            disabled={!graph || busy}
            title="Reset positions to the computed layout"
          >
            <LayoutGrid className="h-4 w-4" /> Auto-layout
          </Button>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <Select value={site} onValueChange={setSite}>
          <SelectTrigger className="w-52" aria-label="Filter by site">
            <SelectValue placeholder="All sites" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All sites</SelectItem>
            {(graph?.groups.sites ?? []).map((s) => (
              <SelectItem key={s.id} value={String(s.id)}>
                {s.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          <Switch
            checked={unlinked === "1"}
            onCheckedChange={(v) => setUnlinked(v ? "1" : "0")}
            aria-label="Show unlinked hosts"
          />
          Unlinked hosts
        </label>
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          <Switch
            checked={overlay}
            onCheckedChange={(v) => setPrefs({ topoHealth: v })}
            aria-label="Health overlay"
          />
          <Activity className="h-3.5 w-3.5" /> Health
        </label>
        <span className="ml-auto hidden text-xs text-muted-foreground md:block">
          click a node for details · double-click to open · drag rearranges
        </span>
      </div>

      {error && (
        <Card>
          <CardContent className="flex items-center justify-between py-6">
            <p className="text-sm text-muted-foreground">
              Couldn&apos;t load the topology — {error}
            </p>
            <Button size="sm" variant="outline" onClick={load}>
              Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {!error && (graph === null || (busy && nodes.length === 0)) && (
        <Skeleton className="min-h-0 flex-1 rounded-lg" />
      )}

      {graph && graph.nodes.length === 0 && !busy && (
        <Card>
          <CardContent className="py-10 text-center text-sm text-muted-foreground">
            Nothing here yet — add devices and cable them, or widen the site
            filter.
          </CardContent>
        </Card>
      )}

      {graph && graph.nodes.length > 0 && (
        <div className="relative min-h-0 flex-1 overflow-hidden rounded-lg border">
          <TopologyMap
            key={layoutNonce}
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onNodeDoubleClick={onNodeDoubleClick}
            onEdgeClick={(edge, at) => {
              setSelected(null);
              setPopup({ edge, x: at.x, y: at.y });
            }}
            onPaneClick={() => {
              setSelected(null);
              setPopup(null);
            }}
            onNodeDragStop={() => setDirty(true)}
          />

          {popup?.edge.data && (
            <div
              className="fixed z-50 w-80 max-w-[90vw] rounded-md border bg-popover p-3 shadow-lg"
              style={{
                left: Math.min(popup.x, window.innerWidth - 340),
                top: Math.min(popup.y, window.innerHeight - 60),
              }}
              role="dialog"
              aria-label="Edge cables"
            >
              <div className="mb-2 flex items-center justify-between">
                <span className="text-sm font-semibold">
                  {popup.edge.data.edge.count} cable
                  {popup.edge.data.edge.count === 1 ? "" : "s"}
                  {popup.edge.data.edge.mismatched && (
                    <Badge variant="red" className="ml-2">
                      ⚠ mismatch
                    </Badge>
                  )}
                </span>
                <button
                  type="button"
                  aria-label="Close"
                  onClick={() => setPopup(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <ul className="max-h-64 space-y-1.5 overflow-y-auto">
                {popup.edge.data.edge.cables.map((c) => (
                  <li
                    key={c.id}
                    className="rounded border bg-card px-2 py-1.5 text-xs"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <a
                        href={`/devices/${c.a_device_id}?trace=${c.a_interface_id}`}
                        className="truncate hover:underline"
                        title={c.a_label}
                      >
                        {c.a_label}
                      </a>
                      <span className="text-muted-foreground">⟷</span>
                      <a
                        href={`/devices/${c.b_device_id}?trace=${c.b_interface_id}`}
                        className="truncate hover:underline"
                        title={c.b_label}
                      >
                        {c.b_label}
                      </a>
                    </div>
                    <div className="mt-0.5 text-muted-foreground">
                      {c.kind}
                      {c.label ? ` · ${c.label}` : ""}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {selected && (
            <div className="absolute right-3 top-3 z-40 w-72 rounded-md border bg-popover p-3 shadow-lg">
              <div className="mb-2 flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="truncate text-sm font-semibold">
                    {selected.label}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {selected.kind === "device"
                      ? (selected.device_type ?? "device")
                      : "unlinked host"}
                  </div>
                </div>
                <button
                  type="button"
                  aria-label="Close"
                  onClick={() => setSelected(null)}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <dl className="space-y-1 text-xs">
                <div className="flex justify-between gap-2">
                  <dt className="text-muted-foreground">Health</dt>
                  <dd>{selected.health}</dd>
                </div>
                {selected.site_id != null && (
                  <div className="flex justify-between gap-2">
                    <dt className="text-muted-foreground">Site</dt>
                    <dd>{siteName(selected.site_id) ?? selected.site_id}</dd>
                  </div>
                )}
                {selected.rack_id != null && (
                  <div className="flex justify-between gap-2">
                    <dt className="text-muted-foreground">Rack</dt>
                    <dd>{rackName(selected.rack_id) ?? selected.rack_id}</dd>
                  </div>
                )}
                {selected.kind === "device" &&
                  selected.interface_count != null && (
                    <div className="flex justify-between gap-2">
                      <dt className="text-muted-foreground">Ports</dt>
                      <dd>
                        {selected.cabled_count}/{selected.interface_count}{" "}
                        cabled
                      </dd>
                    </div>
                  )}
                {selected.hostname && (
                  <div className="flex justify-between gap-2">
                    <dt className="text-muted-foreground">Hostname</dt>
                    <dd className="truncate">{selected.hostname}</dd>
                  </div>
                )}
              </dl>
              <Button
                size="sm"
                variant="outline"
                className="mt-3 w-full"
                onClick={() => router.push(selected.href)}
              >
                Open {selected.kind === "device" ? "device" : "address"}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
