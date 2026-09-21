"use client";

import { Ban, Check, Info, SwatchBook } from "lucide-react";

import { cn } from "@/lib/utils";
import { ROW_COLOR_PALETTE } from "@/lib/row-color";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

/**
 * Global row colors. `row_color` is the manual per-row override shared by
 * all users; `display_color` is what the server resolved (manual beats
 * rule beats none). Everything here renders theme-agnostic — the tint is
 * an alpha overlay + accent bar, never a hardcoded surface.
 */

/** Swatch grid + "None" — embeds inside any DropdownMenuContent (either the
 *  standalone picker below or a submenu in an existing row menu). */
export function RowColorMenuItems({
  value,
  ruled,
  onPick,
}: {
  /** The row's manual color (what the check marks). */
  value: string | null;
  /** True when the row is tinted by a rule with no manual color. */
  ruled?: boolean;
  onPick: (color: string | null) => void;
}) {
  return (
    <>
      <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
        Row color
      </DropdownMenuLabel>
      <div className="grid grid-cols-5 gap-1 px-2 pb-1.5">
        {ROW_COLOR_PALETTE.map((c) => (
          <DropdownMenuItem
            key={c}
            onSelect={() => onPick(c)}
            aria-label={`Set row color ${c}`}
            className={cn(
              "h-7 w-7 rounded-md border-2 p-0",
              value === c ? "border-foreground" : "border-transparent"
            )}
            style={{ background: c }}
          />
        ))}
      </div>
      <DropdownMenuItem
        onSelect={() => onPick(null)}
        aria-label="Clear row color"
        className="gap-2"
      >
        <Ban className="h-3.5 w-3.5" /> None
        {!value && <Check className="ml-auto h-3.5 w-3.5" />}
      </DropdownMenuItem>
      {ruled && (
        <>
          <DropdownMenuSeparator />
          <p className="px-2 py-1 text-xs text-muted-foreground">
            This row is tinted by a rule — picking a color overrides it.
          </p>
        </>
      )}
    </>
  );
}

/** Standalone icon-button swatch popover for the row action group. */
export function RowColorPicker({
  value,
  displayColor,
  name,
  onPick,
}: {
  /** Manual row_color (check-marked swatch). */
  value: string | null;
  /** Effective display_color — tints the trigger icon. */
  displayColor: string | null;
  /** Row name, for the aria-label. */
  name: string;
  onPick: (color: string | null) => void;
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Set color for ${name}`}
        >
          <SwatchBook
            className="h-4 w-4"
            style={displayColor ? { color: displayColor } : undefined}
          />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-44">
        <RowColorMenuItems
          value={value}
          ruled={!value && !!displayColor}
          onPick={onPick}
        />
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/** Legend explaining the precedence — sits in the table toolbar. */
export function RowColorLegend() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-muted-foreground"
          aria-label="How row colors work"
        >
          <Info className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-64">
        <DropdownMenuLabel>Row colors</DropdownMenuLabel>
        <div className="space-y-1.5 px-2 pb-2 text-xs text-muted-foreground">
          <p className="flex items-center gap-2">
            <SwatchBook className="h-3.5 w-3.5 shrink-0" />
            Manual color — set per row, wins over everything.
          </p>
          <p className="flex items-center gap-2">
            <span
              className={cn(
                "h-3.5 w-3.5 shrink-0 rounded-sm",
                "bg-emerald-500/40"
              )}
            />
            Rules — first matching rule (admins: Settings → Color Rules).
          </p>
          <p>No color — the default look.</p>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
