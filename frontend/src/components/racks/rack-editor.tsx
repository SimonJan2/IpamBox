"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
  DndContext,
  PointerSensor,
  pointerWithin,
  useDraggable,
  useDroppable,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragMoveEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { STATUS_TOKENS } from "@/lib/status-tokens";
import { canPlace, conflicts, freeSlots } from "@/lib/rack-collision";
import type { IpStatus, RackDevice, RackFace } from "@/types";
import {
  DeviceBlockSvg,
  HEALTH_KEY,
  RackElevation,
  RackUGrid,
  rackGeom,
  textOn,
  usedUSlots,
  type RackGeom,
} from "@/components/racks/rack-elevation";

/** Saved UI pref for edit mode — same `ipambox:` key namespace as the health
 *  overlay. Viewers never enter edit mode (they get RackElevation). */
const EDIT_KEY = "ipambox:rack-edit";

type Pending = { id: number; u: number; face: RackFace };
type DragSession = {
  id: number;
  height: number;
  face: RackFace;
  free: Set<number>;
};

/** "409: placement conflicts with: sw-a" -> "placement conflicts with: sw-a". */
function errDetail(e: unknown): string {
  const msg = e instanceof Error ? e.message : String(e);
  return msg.replace(/^\d{3}: /, "");
}

/** One U row's drop target — an invisible rect behind the device blocks, so
 *  blocks keep their own pointer handling while empty space reaches the row.
 *  In edit mode it doubles as the "add here" click target and, during a
 *  drag, the valid/invalid tint (green = the dragged device fits, red =
 *  collision or out of range). */
function DropRow({
  u,
  geom,
  tint,
  isPendingU,
  onAdd,
}: {
  u: number;
  geom: RackGeom;
  tint: "free" | "blocked" | null;
  isPendingU: boolean;
  onAdd: () => void;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: u });
  return (
    <rect
      ref={(el) => setNodeRef(el as unknown as HTMLElement)}
      x={geom.NUM_W}
      y={geom.uTop(u) + 1}
      width={geom.W - geom.NUM_W - 4}
      height={geom.U - 2}
      rx={2}
      className={cn(
        "cursor-pointer transition-colors",
        tint === "free"
          ? "fill-emerald-500/15"
          : tint === "blocked"
            ? "fill-rose-500/10"
            : "fill-transparent hover:fill-emerald-500/10",
        isPendingU && "fill-sky-500/20",
        isOver && tint === "free" && "fill-emerald-500/30",
        isOver && tint === "blocked" && "fill-rose-500/25"
      )}
      onClick={onAdd}
    />
  );
}

/** A device block wired for editing: draggable + focusable with arrow-key
 *  moves while `edit` is on; a plain selectable block otherwise. */
function EditorBlock({
  d,
  geom,
  health,
  edit,
  selected,
  pending,
  pendingValid,
  focused,
  suppressClick,
  onSelect,
  onKeyMove,
  onFocus,
  onBlur,
}: {
  d: RackDevice;
  geom: RackGeom;
  health: boolean;
  edit: boolean;
  selected: boolean;
  /** Keyboard-move preview for this block (null when it's not moving). */
  pending: { u: number; face: RackFace } | null;
  pendingValid: boolean;
  focused: boolean;
  suppressClick: { current: boolean };
  onSelect?: (d: RackDevice | null) => void;
  onKeyMove: (d: RackDevice, e: React.KeyboardEvent<SVGGElement>) => void;
  onFocus: () => void;
  onBlur: () => void;
}) {
  const { attributes, listeners, setNodeRef, isDragging } = useDraggable({
    id: d.id,
    disabled: !edit,
  });
  const top = (pending?.u ?? d.u_position) + d.u_height - 1;
  const span = `U${pending?.u ?? d.u_position}${d.u_height > 1 ? `–${top}` : ""}`;
  const face = pending?.face ?? d.face;
  const label = edit
    ? pending
      ? `${d.name} — ${span}, ${face}. Enter commits, Escape cancels.`
      : `${d.name} — ${span}, ${face}. Arrow keys move, Enter selects.`
    : `${d.name} — ${span}, ${face}`;
  return (
    <DeviceBlockSvg
      d={d}
      geom={geom}
      health={health}
      selected={selected}
      u={pending?.u}
      face={pending?.face}
      ghost={
        isDragging ? "drag" : pending ? (pendingValid ? "ok" : "bad") : null
      }
      focused={edit && focused}
      ref={(el: SVGGElement | null) =>
        setNodeRef(el as unknown as HTMLElement)
      }
      {...(edit ? { ...attributes, ...listeners } : {})}
      onClick={() => {
        if (!suppressClick.current) onSelect?.(selected ? null : d);
      }}
      onKeyDown={edit ? (e) => onKeyMove(d, e) : undefined}
      onFocus={edit ? onFocus : undefined}
      onBlur={edit ? onBlur : undefined}
      className={cn(
        "outline-none",
        edit
          ? "cursor-grab touch-none active:cursor-grabbing"
          : onSelect && "cursor-pointer"
      )}
      role={edit || onSelect ? "button" : undefined}
      tabIndex={edit ? 0 : undefined}
      aria-label={label}
    />
  );
}

/**
 * Editable rack elevation — same drawing as RackElevation plus an Edit mode
 * (persisted): drag devices between U slots, arrow-key moves with live
 * collision gating, click an empty slot to add a device there. Dropping on
 * the rear view places the device on the rear face (and vice versa), unless
 * it's `both`. All moves are optimistic; the backend stays authoritative —
 * a 409 reverts the move and toasts the server's conflict message.
 */
export function RackEditor({
  rackId,
  name,
  heightU,
  devices,
  setDevices,
  selectedId = null,
  onSelect,
  canWrite,
  onAddAt,
}: {
  rackId: number;
  name: string;
  heightU: number;
  devices: RackDevice[];
  /** Optimistic device-list mutation owned by the caller. */
  setDevices: (fn: (ds: RackDevice[]) => RackDevice[]) => void;
  selectedId?: number | null;
  onSelect?: (d: RackDevice | null) => void;
  canWrite: boolean;
  /** Click-empty-slot in edit mode — open the device form prefilled. */
  onAddAt?: (u: number, face: RackFace) => void;
}) {
  const [view, setView] = useState<"front" | "rear">("front");
  const [health, setHealth] = useState(true);
  const [edit, setEdit] = useState(false);
  const [pending, setPending] = useState<Pending | null>(null);
  const [drag, setDrag] = useState<DragSession | null>(null);
  const [overU, setOverU] = useState<number | null>(null);
  const [focusId, setFocusId] = useState<number | null>(null);
  const [announce, setAnnounce] = useState("");
  /** Swallows the click a drop gesture also fires (block + drop row). */
  const suppressClick = useRef(false);
  /** Serializes PATCHes so back-to-back moves can't reorder on the wire. */
  const queue = useRef<Promise<unknown>>(Promise.resolve());

  useEffect(() => {
    try {
      if (localStorage.getItem(HEALTH_KEY) === "0") setHealth(false);
      if (canWrite && localStorage.getItem(EDIT_KEY) === "1") setEdit(true);
    } catch {}
  }, [canWrite]);

  const geom = rackGeom(heightU);
  const visible = useMemo(
    () => devices.filter((d) => d.face === "both" || d.face === view),
    [devices, view]
  );
  const usedU = usedUSlots(devices);
  const pendDev = pending ? devices.find((d) => d.id === pending.id) : null;
  const pendValid = !!(
    pendDev &&
    pending &&
    canPlace(
      devices,
      { ...pendDev, u_position: pending.u, face: pending.face },
      heightU
    )
  );
  /** Rows tinted while dragging or while a keyboard move is pending. */
  const tintFree =
    drag?.free ??
    (pendDev && pending
      ? freeSlots(devices, heightU, pendDev.u_height, pending.face, pending.id)
      : null);
  const dragDev = drag ? devices.find((d) => d.id === drag.id) : null;

  const spanLabel = (u: number, h: number) =>
    `U${u}${h > 1 ? `–${u + h - 1}` : ""}`;

  const apply = (id: number, patch: Partial<RackDevice>) =>
    setDevices((ds) => ds.map((x) => (x.id === id ? { ...x, ...patch } : x)));

  const enqueue = (job: () => Promise<unknown>) => {
    queue.current = queue.current.then(job).catch(() => {});
  };

  /** PATCH u_position+face; on failure restore `back` and toast the server's
   *  conflict message (409/422 both land here — the server stays right). */
  const save = async (
    id: number,
    body: { u_position: number; face: RackFace },
    back: { u_position: number; face: RackFace }
  ): Promise<boolean> => {
    try {
      const saved = await api.patch<RackDevice>(
        `/api/v1/racks/${rackId}/devices/${id}`,
        body
      );
      setDevices((ds) => ds.map((x) => (x.id === id ? saved : x)));
      return true;
    } catch (e) {
      apply(id, back);
      toast.error("Move rejected", { description: errDetail(e) });
      setAnnounce(`Move rejected: ${errDetail(e)}`);
      return false;
    }
  };

  const commitMove = (d: RackDevice, u: number, face: RackFace) => {
    if (u === d.u_position && face === d.face) return;
    const back = { u_position: d.u_position, face: d.face };
    const next = { u_position: u, face };
    apply(d.id, next);
    enqueue(async () => {
      if (!(await save(d.id, next, back))) return;
      const faceNote =
        face !== d.face ? ` — moved to ${face} face` : "";
      toast.success(`${d.name} → U${u}${faceNote}`, {
        action: {
          label: "Undo",
          onClick: () => {
            apply(d.id, back);
            enqueue(() => save(d.id, back, next));
          },
        },
      });
      setAnnounce(`${d.name} moved to ${spanLabel(u, d.u_height)}${faceNote}`);
    });
  };

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
    if (!next) {
      setPending(null);
      setDrag(null);
      setOverU(null);
    }
    setAnnounce(
      next
        ? "Edit mode — drag devices, or focus a device and use arrow keys"
        : "View mode"
    );
  };

  const sensors = useSensors(
    // 4px of travel before a drag starts, so plain clicks still select.
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } })
  );

  const onDragStart = (e: DragStartEvent) => {
    const d = devices.find((x) => x.id === Number(e.active.id));
    if (!d) return;
    setPending(null);
    // Drop semantics: the view decides the face unless the device is `both`.
    const face: RackFace = d.face === "both" ? "both" : view;
    setDrag({
      id: d.id,
      height: d.u_height,
      face,
      free: freeSlots(devices, heightU, d.u_height, face, d.id),
    });
    setAnnounce(
      `Dragging ${d.name} (${spanLabel(d.u_position, d.u_height)}, ${face} face)`
    );
  };

  const onDragMove = (e: DragMoveEvent) =>
    setOverU(e.over ? Number(e.over.id) : null);

  const onDragEnd = (e: DragEndEvent) => {
    suppressClick.current = true;
    setTimeout(() => {
      suppressClick.current = false;
    }, 0);
    const d = devices.find((x) => x.id === Number(e.active.id));
    const u = e.over ? Number(e.over.id) : null;
    const session = drag;
    setDrag(null);
    setOverU(null);
    if (!d || !session || u === null) return;
    if (session.free.has(u)) {
      commitMove(d, u, session.face);
    } else {
      const names = conflicts(devices, {
        ...d,
        u_position: u,
        face: session.face,
      })
        .map((x) => x.name)
        .join(", ");
      setAnnounce(
        `U${u} blocked${names ? ` — conflicts with ${names}` : ""}; ${d.name} stays at ${spanLabel(d.u_position, d.u_height)}`
      );
    }
  };

  const onDragCancel = () => {
    setDrag(null);
    setOverU(null);
  };

  /** Arrow/Enter/Esc/F/B handling on a focused device block. Arrows jump to
   *  the next U where canPlace passes (invalid slots are skipped over); the
   *  preview lives in `pending` until Enter commits or Esc cancels. */
  const keyMove = (d: RackDevice, e: React.KeyboardEvent<SVGGElement>) => {
    if (!edit) return;
    const k = e.key;
    if (
      !["ArrowUp", "ArrowDown", "Enter", "Escape", "f", "F", "b", "B"].includes(k)
    ) {
      return;
    }
    e.preventDefault();
    e.stopPropagation();
    const cur: Pending =
      pending?.id === d.id
        ? pending
        : { id: d.id, u: d.u_position, face: d.face };

    if (k === "Escape") {
      if (pending?.id === d.id) {
        setPending(null);
        setAnnounce(
          `${d.name} stays at ${spanLabel(d.u_position, d.u_height)} — move cancelled`
        );
      }
      return;
    }
    if (k === "Enter") {
      if (pending?.id !== d.id) {
        onSelect?.(d.id === selectedId ? null : d);
        return;
      }
      const cand = { ...d, u_position: pending.u, face: pending.face };
      if (canPlace(devices, cand, heightU)) {
        const { u, face } = pending;
        setPending(null);
        commitMove(d, u, face);
      } else {
        const names = conflicts(devices, cand)
          .map((x) => x.name)
          .join(", ");
        setAnnounce(
          `U${pending.u} blocked${names ? ` — conflicts with ${names}` : ""}`
        );
      }
      return;
    }
    const lc = k.toLowerCase();
    if (lc === "f" || lc === "b") {
      const face: RackFace = lc === "f" ? "front" : "rear";
      const ok = canPlace(
        devices,
        { ...d, u_position: cur.u, face },
        heightU
      );
      setPending({ ...cur, face });
      setAnnounce(
        `${d.name} face → ${face}${ok ? "" : ` — U${cur.u} now conflicts`}`
      );
      return;
    }
    const delta = k === "ArrowUp" ? 1 : -1;
    const maxStart = heightU - d.u_height + 1;
    let u = cur.u + delta;
    while (
      u >= 1 &&
      u <= maxStart &&
      !canPlace(devices, { ...d, u_position: u, face: cur.face }, heightU)
    ) {
      u += delta;
    }
    if (u < 1 || u > maxStart) {
      setAnnounce(
        `No free U ${delta > 0 ? "above" : "below"} for ${d.name}`
      );
      return;
    }
    setPending({ ...cur, u });
    setAnnounce(
      `${d.name} → ${spanLabel(u, d.u_height)} — Enter commits, Esc cancels`
    );
  };

  if (!canWrite) {
    return (
      <RackElevation
        name={name}
        heightU={heightU}
        devices={devices}
        selectedId={selectedId}
        onSelect={onSelect}
      />
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={pointerWithin}
      onDragStart={onDragStart}
      onDragMove={onDragMove}
      onDragEnd={onDragEnd}
      onDragCancel={onDragCancel}
    >
      <div className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <div className={cn("min-w-0", edit && "opacity-60")}>
            <span dir="auto" className="font-medium">
              {name}
            </span>
            <span className="ml-2 text-sm text-muted-foreground">
              {usedU}/{heightU}U used
            </span>
          </div>
          <div className="flex items-center gap-2 print:hidden">
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
            <button
              type="button"
              aria-pressed={edit}
              onClick={toggleEdit}
              title="Move devices by dragging or with arrow keys"
              className={cn(
                "rounded-lg border px-3 py-1 text-sm transition-colors",
                edit
                  ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-400"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              Edit
            </button>
            <div
              role="group"
              aria-label="Rack face"
              className="flex rounded-lg border p-0.5"
            >
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
          </div>
        </div>

        <svg
          viewBox={`0 0 ${geom.W} ${geom.H}`}
          className="w-full max-w-sm rounded-lg border bg-card"
          role={edit ? "application" : "img"}
          aria-label={`${view} elevation of ${name}${edit ? " — editing" : ""}`}
        >
          <RackUGrid heightU={heightU} geom={geom} />

          {edit &&
            Array.from({ length: heightU }, (_, i) => {
              const u = i + 1;
              return (
                <DropRow
                  key={u}
                  u={u}
                  geom={geom}
                  tint={tintFree ? (tintFree.has(u) ? "free" : "blocked") : null}
                  isPendingU={pending?.u === u}
                  onAdd={() => {
                    if (!suppressClick.current) onAddAt?.(u, view);
                  }}
                />
              );
            })}

          {visible.map((d) => (
            <EditorBlock
              key={d.id}
              d={d}
              geom={geom}
              health={health}
              edit={edit}
              selected={d.id === selectedId}
              pending={pending?.id === d.id ? pending : null}
              pendingValid={pendValid}
              focused={focusId === d.id}
              suppressClick={suppressClick}
              onSelect={onSelect}
              onKeyMove={keyMove}
              onFocus={() => setFocusId(d.id)}
              onBlur={() => {
                setFocusId((f) => (f === d.id ? null : f));
                if (pending?.id === d.id) setPending(null);
              }}
            />
          ))}

          {drag &&
            dragDev &&
            overU !== null &&
            overU <= heightU - drag.height + 1 && (
              <g className="pointer-events-none">
                <rect
                  x={geom.NUM_W + 2}
                  y={geom.blockY(overU, drag.height)}
                  width={geom.W - geom.NUM_W - 8}
                  height={drag.height * geom.U - 2}
                  rx={2}
                  fill={dragDev.colour ?? "#334155"}
                  fillOpacity={0.4}
                  className={
                    drag.free.has(overU)
                      ? "stroke-emerald-400"
                      : "stroke-rose-400"
                  }
                  strokeWidth={1.5}
                  strokeDasharray="4 2"
                />
                <text
                  x={geom.NUM_W + 2 + (geom.W - geom.NUM_W - 8) / 2}
                  y={geom.blockY(overU, drag.height) + (drag.height * geom.U - 2) / 2}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fill={textOn(dragDev.colour)}
                  fontSize={Math.min(11, Math.max(8, geom.U * 0.5))}
                >
                  {dragDev.name}
                </text>
              </g>
            )}
        </svg>

        {edit && (
          <p className="max-w-sm text-xs text-muted-foreground">
            Drag a device onto a U slot — green fits, red conflicts. Or focus a
            block: ↑/↓ moves (skipping blocked slots), F/B sets the face,
            Enter commits, Esc cancels. Click an empty slot to add a device.
          </p>
        )}

        {health && (
          <div
            className={cn(
              "flex max-w-sm flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground",
              edit && "opacity-60"
            )}
          >
            {(Object.keys(STATUS_TOKENS) as IpStatus[]).map((s) => (
              <span key={s} className="inline-flex items-center gap-1">
                <span
                  className={cn("h-2 w-2 rounded-full", STATUS_TOKENS[s].dot)}
                />
                {s}
              </span>
            ))}
            <span className="inline-flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />
              unmonitored
            </span>
          </div>
        )}

        <div role="status" aria-live="polite" className="sr-only">
          {announce}
        </div>
      </div>
    </DndContext>
  );
}
