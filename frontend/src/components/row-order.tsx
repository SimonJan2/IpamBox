"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  type ComponentProps,
  type ReactNode,
} from "react";
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { GripVertical, Pin } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { TableCell, TableRow } from "@/components/ui/table";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

// Shared DnD bits for the entity list pages. Row order is global state
// (Postgres) — these components only handle gesture + presentation; the
// useRowOrder hook owns optimistic updates and persistence.

/** DndContext + SortableContext around a <Table> (renders no DOM). `ids`
 *  must be the visible row ids in display order. */
export function RowOrderDnd({
  ids,
  onDragEnd,
  children,
}: {
  ids: number[];
  onDragEnd: (e: DragEndEvent) => void;
  children: ReactNode;
}) {
  const sensors = useSensors(
    // 4px of travel before a drag starts, so plain clicks still reach the
    // row and its buttons.
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );
  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={onDragEnd}
    >
      <SortableContext items={ids} strategy={verticalListSortingStrategy}>
        {children}
      </SortableContext>
    </DndContext>
  );
}

type HandleState = {
  attributes: ReturnType<typeof useSortable>["attributes"];
  listeners: ReturnType<typeof useSortable>["listeners"];
  disabled: boolean;
};

const HandleCtx = createContext<HandleState | null>(null);

type SortableRowProps = ComponentProps<typeof TableRow> & {
  /** The entity id — must be one of RowOrderDnd's `ids`. */
  rowId: number;
  /** True while a sort/filter is active or the user can't write. */
  dragDisabled?: boolean;
};

/** A <TableRow> that participates in sortable ordering. Accepts row-nav's
 *  rowProps (its `ref` is merged with dnd-kit's node ref — React 19 passes
 *  ref through as a normal prop). */
export function SortableRow({
  rowId,
  dragDisabled,
  className,
  style,
  children,
  ...rest
}: SortableRowProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: rowId, disabled: !!dragDisabled });
  const { ref: navRef, ...trProps } = rest;
  const setRefs = useCallback(
    (el: HTMLTableRowElement | null) => {
      setNodeRef(el);
      if (typeof navRef === "function") navRef(el);
      else if (navRef) navRef.current = el;
    },
    [setNodeRef, navRef]
  );
  const handle = useMemo<HandleState>(
    () => ({ attributes, listeners, disabled: !!dragDisabled }),
    [attributes, listeners, dragDisabled]
  );
  return (
    <HandleCtx.Provider value={handle}>
      <TableRow
        ref={setRefs}
        data-dragging={isDragging || undefined}
        style={{
          // Caller styles (row-color tint) merge with — never clobber — the
          // dnd transform.
          ...(transform
            ? {
                transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
                transition,
              }
            : { transition }),
          ...style,
        }}
        className={cn(className, isDragging && "relative z-10 bg-muted")}
        {...trProps}
      >
        {children}
      </TableRow>
    </HandleCtx.Provider>
  );
}

/** Grip handle for a SortableRow. Renders inert (with an explanatory
 *  tooltip) while ordering is disabled. */
export function DragHandle({
  reason,
  label,
}: {
  /** Why dragging is off right now (sort/filter active) — shown as a
   *  tooltip. Omit when enabled. */
  reason?: string | null;
  /** aria-label, e.g. `Reorder site DC-East`. */
  label: string;
}) {
  const ctx = useContext(HandleCtx);
  const disabled = !ctx || ctx.disabled;
  const btn = (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      aria-label={label}
      {...(ctx?.attributes ?? {})}
      {...(disabled ? {} : ctx?.listeners)}
      tabIndex={disabled ? -1 : 0}
      className={cn(
        "h-7 w-7 touch-none",
        disabled
          ? "cursor-not-allowed text-muted-foreground/40"
          : "cursor-grab text-muted-foreground active:cursor-grabbing"
      )}
    >
      <GripVertical className="h-4 w-4" />
    </Button>
  );
  if (disabled && reason) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>{btn}</TooltipTrigger>
        <TooltipContent>{reason}</TooltipContent>
      </Tooltip>
    );
  }
  return btn;
}

/** Pin/unpin action button for the row action group. */
export function PinToggle({
  pinned,
  name,
  onToggle,
}: {
  pinned: boolean;
  /** Row name, for the aria-label. */
  name: string;
  onToggle: () => void;
}) {
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={pinned ? `Unpin ${name}` : `Pin ${name}`}
      aria-pressed={pinned}
      onClick={onToggle}
    >
      <Pin
        className={cn("h-4 w-4", pinned && "text-sky-400")}
        fill={pinned ? "currentColor" : "none"}
      />
    </Button>
  );
}

/** Section header rendered above pinned rows (default order only). */
export function PinnedDivider({ colSpan }: { colSpan: number }) {
  return (
    <TableRow className="bg-muted/40 hover:bg-muted/40">
      <TableCell
        colSpan={colSpan}
        className="py-1.5 text-xs font-medium text-muted-foreground"
      >
        <span className="inline-flex items-center gap-1.5">
          <Pin className="h-3.5 w-3.5" /> Pinned
        </span>
      </TableCell>
    </TableRow>
  );
}
