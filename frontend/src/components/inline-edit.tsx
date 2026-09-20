"use client";

import { useEffect, useRef, useState } from "react";
import { Loader2 } from "lucide-react";

import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";

/**
 * Click-to-edit table cells. Enter/blur commits, Esc cancels, and the cell
 * shows a spinner while `onSave` is in flight. The parent owns the data
 * (optimistic update + rollback on rejection); `onSave` should reject on
 * failure so the editor stays open. `disabled` renders plain read-only text.
 */
export function InlineText({
  value,
  onSave,
  disabled,
  label,
  dir,
  empty = "—",
  className,
}: {
  value: string | null;
  onSave: (v: string) => Promise<void>;
  disabled?: boolean;
  label: string;
  dir?: "auto" | "ltr";
  empty?: string;
  className?: string;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value ?? "");
  const [busy, setBusy] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  const commit = async () => {
    const v = draft.trim();
    if (v === (value ?? "")) {
      setEditing(false);
      return;
    }
    setBusy(true);
    try {
      await onSave(v);
      setEditing(false);
    } catch {
      /* parent rolled back + toasted; keep editing */
    } finally {
      setBusy(false);
    }
  };

  if (disabled) {
    return (
      <span dir={dir} className={cn("text-muted-foreground", className)}>
        {value || empty}
      </span>
    );
  }

  if (!editing) {
    return (
      <button
        type="button"
        onClick={() => {
          setDraft(value ?? "");
          setEditing(true);
        }}
        aria-label={label}
        title="Click to edit"
        dir={dir}
        className={cn(
          "-m-1 block max-w-full truncate rounded p-1 text-left text-muted-foreground hover:bg-muted/60 hover:text-foreground focus-visible:bg-muted/60 focus-visible:outline-none",
          className
        )}
      >
        {value || empty}
      </button>
    );
  }

  return (
    <span className="relative block">
      <Input
        ref={inputRef}
        dir={dir}
        aria-label={label}
        value={draft}
        disabled={busy}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={() => void commit()}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            void commit();
          } else if (e.key === "Escape") {
            e.preventDefault();
            e.stopPropagation();
            setEditing(false);
          }
        }}
        className="h-7 px-1.5 text-sm"
      />
      {busy && (
        <Loader2 className="absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 animate-spin text-muted-foreground" />
      )}
    </span>
  );
}

/** Click-to-edit select cell — opens a compact dropdown on click. */
export function InlineSelect<T extends string>({
  value,
  options,
  onSave,
  disabled,
  label,
  display,
}: {
  value: T;
  options: readonly T[];
  onSave: (v: T) => Promise<void>;
  disabled?: boolean;
  label: string;
  /** Renders the current value when idle; defaults to the raw value. */
  display?: (v: T) => React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  if (disabled) return <>{display ? display(value) : value}</>;
  if (busy) {
    return (
      <Loader2 className="h-3.5 w-3.5 animate-spin text-muted-foreground" />
    );
  }

  return (
    <Select
      value={value}
      open={open}
      onOpenChange={setOpen}
      onValueChange={async (v: string) => {
        if (v === value) return;
        setBusy(true);
        try {
          await onSave(v as T);
        } catch {
          /* parent rolled back + toasted */
        } finally {
          setBusy(false);
        }
      }}
    >
      <SelectTrigger
        aria-label={label}
        title="Click to edit"
        className="h-auto w-auto gap-1.5 border-0 bg-transparent p-0 shadow-none hover:bg-transparent focus:ring-1 focus:ring-offset-0 [&>svg]:h-3 [&>svg]:w-3"
      >
        <span>{display ? display(value) : value}</span>
      </SelectTrigger>
      <SelectContent>
        {options.map((o) => (
          <SelectItem key={o} value={o}>
            {o}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
