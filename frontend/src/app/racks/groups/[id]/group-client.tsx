"use client";

/** Bayed-row view of a rack group: member racks ordered by group_position,
 *  rendered side by side on a shared floor line inside a horizontal strip.
 *
 *  Read-mostly by design — one Health toggle and a front/rear face toggle
 *  mirror the single-rack elevation. With data:write, an Edit toggle turns
 *  the strip into a DndContext spanning every column, so a device dragged
 *  sideways lands on another rack's U row (PATCH rack_id + u_position; the
 *  backend re-validates placement and mounted children come along with a
 *  moved carrier). Cross-rack carrier-slot drops are out of scope — a child
 *  dropped on a U row unmounts, matching the rack editor. */
import { useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft, Boxes } from "lucide-react";
import {
  DndContext,
  PointerSensor,
  pointerWithin,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { cn } from "@/lib/utils";
import { STATUS_TOKENS } from "@/lib/status-tokens";
import type { IpStatus, Page, RackDetail, RackDevice, RackGroupDetail, Site } from "@/types";
import { deviceSums, formatKg, formatWatts } from "@/lib/rack-capacity";
import { HEALTH_KEY, usedUSlots } from "@/components/racks/rack-elevation";
import {
  freeByRack,
  parseRowDev,
  parseRowDrop,
  RackRowColumn,
} from "@/components/racks/rack-row";
import { AsyncPanel } from "@/components/async-panel";
import { DocsLink } from "@/components/docs/docs-link";
import { Button } from "@/components/ui/button";

const EDIT_KEY = "ipambox:rack-group-edit";

type DragSession = {
  id: number;
  srcRackId: number;
  height: number;
  free: Map<number, Set<number>>;
};

function errDetail(e: unknown): string {
  const msg = e instanceof Error ? e.message : String(e);
  return msg.replace(/^\d{3}: /, "");
}

/** Locate a device inside the group's racks. */
function findDevice(
  racks: RackDetail[],
  id: number
): { device: RackDevice; rack: RackDetail } | null {
  for (const rack of racks) {
    const device = rack.devices.find((d) => d.id === id);
    if (device) return { device, rack };
  }
  return null;
}

/** Pure optimistic move: splice `id` (plus its mounted children when it's a
 *  carrier) into `toRack` at `u`, clearing any carrier mount — mirrors the
 *  server-side move semantics so the strip re-renders instantly. */
function moveDevice(
  racks: RackDetail[],
  id: number,
  toRackId: number,
  u: number
): RackDetail[] {
  const hit = findDevice(racks, id);
  if (!hit) return racks;
  const { device } = hit;
  const moving = new Set<number>([
    id,
    ...racks
      .flatMap((r) => r.devices)
      .filter((d) => d.carrier_id === id)
      .map((d) => d.id),
  ]);
  return racks.map((r) => {
    let devices = r.devices.filter((d) => !moving.has(d.id));
    if (r.id === toRackId) {
      devices = [
        ...devices,
        { ...device, rack_id: toRackId, u_position: u, carrier_id: null, slot: null },
        ...racks
          .flatMap((x) => x.devices)
          .filter((d) => d.carrier_id === id)
          .map((c) => ({ ...c, rack_id: toRackId, u_position: u, face: device.face })),
      ];
    }
    return { ...r, devices };
  });
}

export default function GroupClient({ id }: { id: string }) {
  const router = useRouter();
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);

  const groupQ = useAsyncData(
    () => api.get<RackGroupDetail>(`/api/v1/rack-groups/${id}`),
    [id]
  );
  const sitesQ = useAsyncData(async () => {
    try {
      return await api.get<Page<Site>>("/api/v1/sites").then((p) => p.items);
    } catch {
      return [];
    }
  });

  const [view, setView] = useState<"front" | "rear">("front");
  const [health, setHealth] = useState(true);
  const [edit, setEdit] = useState(false);
  const [drag, setDrag] = useState<DragSession | null>(null);
  const [announce, setAnnounce] = useState("");
  const queue = useRef<Promise<unknown>>(Promise.resolve());

  useEffect(() => {
    try {
      if (localStorage.getItem(HEALTH_KEY) === "0") setHealth(false);
      if (canWrite && localStorage.getItem(EDIT_KEY) === "1") setEdit(true);
    } catch {}
  }, [canWrite]);

  const group = groupQ.data;
  const racks = useMemo(() => group?.racks ?? [], [group]);

  const siteName = group?.site_id
    ? (sitesQ.data ?? []).find((s) => s.id === group.site_id)?.name
    : null;

  const totals = useMemo(() => {
    const used = racks.reduce((s, r) => s + usedUSlots(r.devices), 0);
    const height = racks.reduce((s, r) => s + r.height_u, 0);
    let watts: number | null = null;
    let kg: number | null = null;
    for (const r of racks) {
      const s = deviceSums(r.devices);
      if (s.watts != null) watts = (watts ?? 0) + s.watts;
      if (s.kg != null) kg = Math.round(((kg ?? 0) + s.kg) * 100) / 100;
    }
    return { used, free: Math.max(height - used, 0), height, watts, kg };
  }, [racks]);

  const toggleHealth = () =>
    setHealth((h) => {
      const next = !h;
      try {
        localStorage.setItem(HEALTH_KEY, next ? "1" : "0");
      } catch {}
      return next;
    });

  const toggleEdit = () => {
    const next = !edit;
    setEdit(next);
    try {
      localStorage.setItem(EDIT_KEY, next ? "1" : "0");
    } catch {}
    if (!next) setDrag(null);
    setAnnounce(
      next
        ? "Edit mode — drag a device sideways onto another rack's U row"
        : "View mode"
    );
  };

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } })
  );

  const onDragStart = (e: DragStartEvent) => {
    const devId = parseRowDev(e.active.id);
    if (devId == null) return;
    const hit = findDevice(racks, devId);
    if (!hit) return;
    setDrag({
      id: devId,
      srcRackId: hit.rack.id,
      height: hit.device.u_height,
      free: freeByRack(racks, hit.device),
    });
    setAnnounce(`Dragging ${hit.device.name}`);
  };

  const enqueue = (job: () => Promise<unknown>) => {
    queue.current = queue.current.then(job).catch(() => {});
  };

  const onDragEnd = (e: DragEndEvent) => {
    const devId = parseRowDev(e.active.id);
    const target = e.over ? parseRowDrop(e.over.id) : null;
    const session = drag;
    setDrag(null);
    if (devId == null || !target || !session || !group) return;
    const hit = findDevice(racks, devId);
    if (!hit) return;
    const { device, rack: srcRack } = hit;
    const { rackId: dstRackId, u } = target;
    const dstRack = racks.find((r) => r.id === dstRackId);
    if (!dstRack) return;
    const unchanged =
      srcRack.id === dstRackId &&
      u === device.u_position &&
      device.carrier_id == null;
    if (unchanged) return;
    if (!session.free.get(dstRackId)?.has(u)) {
      setAnnounce(
        `U${u} on ${dstRack.name} is blocked — ${device.name} stays at U${device.u_position}`
      );
      return;
    }

    const before = racks;
    const label =
      srcRack.id === dstRackId
        ? `${device.name} moved to U${u}`
        : `${device.name} moved to ${dstRack.name} U${u}`;
    groupQ.setData((cur) =>
      cur ? { ...cur, racks: moveDevice(cur.racks, devId, dstRackId, u) } : cur
    );
    enqueue(async () => {
      try {
        await api.patch<RackDevice>(
          `/api/v1/racks/${srcRack.id}/devices/${devId}`,
          {
            rack_id: dstRackId,
            u_position: u,
            carrier_id: null,
            slot: null,
          }
        );
        toast.success(label);
        setAnnounce(label);
      } catch (err) {
        groupQ.setData((cur) => (cur ? { ...cur, racks: before } : cur));
        toast.error("Move rejected", { description: errDetail(err) });
        setAnnounce(`Move rejected: ${errDetail(err)}`);
      }
    });
  };

  const onOpenRack = (rackId: number, deviceId: number) => {
    router.push(`/racks/${rackId}?device=${deviceId}`);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="flex items-center gap-1.5 text-xl font-semibold">
          <Button variant="ghost" size="icon" asChild aria-label="Back to racks">
            <Link href="/racks">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <Boxes className="h-5 w-5 text-muted-foreground" />
          <span dir="auto">{group?.name ?? "Rack group"}</span>
          {group && (
            <span className="text-sm font-normal text-muted-foreground">
              {racks.length} rack{racks.length === 1 ? "" : "s"}
              {siteName ? ` · ${siteName}` : ""}
            </span>
          )}
          <DocsLink slug="racks" />
        </h1>
        <div className="flex items-center gap-2">
          <button
            type="button"
            aria-pressed={health}
            onClick={toggleHealth}
            title="Overlay linked-IP scan health"
            className={cn(
              "rounded-lg border px-3 py-1 text-sm transition-colors",
              health
                ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-400"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            Health
          </button>
          <div role="group" aria-label="Rack face" className="flex rounded-lg border p-0.5">
            {(["front", "rear"] as const).map((v) => (
              <button
                key={v}
                type="button"
                onClick={() => setView(v)}
                className={cn(
                  "rounded-md px-3 py-1 text-sm capitalize transition-colors",
                  view === v
                    ? "bg-emerald-500/15 text-emerald-400"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                {v}
              </button>
            ))}
          </div>
          {canWrite && (
            <button
              type="button"
              aria-pressed={edit}
              onClick={toggleEdit}
              title="Drag devices between racks"
              className={cn(
                "rounded-lg border px-3 py-1 text-sm transition-colors",
                edit
                  ? "border-sky-500/40 bg-sky-500/15 text-sky-400"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              Edit
            </button>
          )}
        </div>
      </div>

      {group?.description && (
        <p dir="auto" className="text-sm text-muted-foreground">
          {group.description}
        </p>
      )}

      {group && (
        <div className="flex flex-wrap gap-x-5 gap-y-1 rounded-lg border bg-card px-4 py-2.5 text-sm">
          <span>
            <span className="font-medium">{totals.used}</span>
            <span className="text-muted-foreground">/{totals.height} U used</span>
            {totals.free > 0 && (
              <span className="text-muted-foreground"> · {totals.free} free</span>
            )}
          </span>
          {totals.watts != null && (
            <span className="text-muted-foreground">
              Σ {formatWatts(totals.watts)}
            </span>
          )}
          {totals.kg != null && (
            <span className="text-muted-foreground">
              Σ {formatKg(totals.kg)}
            </span>
          )}
        </div>
      )}

      <AsyncPanel
        loading={groupQ.loading}
        error={groupQ.error}
        onRetry={groupQ.reload}
        empty={!group}
        emptyMessage="Rack group not found."
      >
        <DndContext
          sensors={sensors}
          collisionDetection={pointerWithin}
          onDragStart={onDragStart}
          onDragEnd={onDragEnd}
          onDragCancel={() => setDrag(null)}
        >
          <div className="flex items-end gap-4 overflow-x-auto pb-2">
            {racks.map((r) => (
              <RackRowColumn
                key={r.id}
                rack={r}
                view={view}
                health={health}
                edit={edit}
                tint={drag ? drag.free.get(r.id) ?? new Set() : null}
                onOpenRack={onOpenRack}
              />
            ))}
            {racks.length === 0 && (
              <p className="py-10 text-sm text-muted-foreground">
                No racks in this group yet — assign racks from the racks list.
              </p>
            )}
          </div>
        </DndContext>
      </AsyncPanel>

      {health && racks.length > 0 && (
        <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground">
          {(Object.keys(STATUS_TOKENS) as IpStatus[]).map((s) => (
            <span key={s} className="inline-flex items-center gap-1">
              <span className={cn("h-2 w-2 rounded-full", STATUS_TOKENS[s].dot)} />
              {s}
            </span>
          ))}
          <span className="inline-flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />
            unmonitored
          </span>
        </div>
      )}

      <div aria-live="polite" className="sr-only">
        {announce}
      </div>
    </div>
  );
}
