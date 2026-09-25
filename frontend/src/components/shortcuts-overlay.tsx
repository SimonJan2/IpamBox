"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

const IS_MAC =
  typeof navigator !== "undefined" &&
  /Mac|iPhone|iPad/.test(navigator.platform);

interface Group {
  name: string;
  items: [keys: string, action: string][];
}

const GROUPS: Group[] = [
  {
    name: "Global",
    items: [
      [IS_MAC ? "⌘K" : "Ctrl K", "Search (toggle)"],
      ["/", "Search"],
      ["?", "This overlay"],
    ],
  },
  {
    name: "Go to (press g, then the key)",
    items: [
      ["g d", "Dashboard"],
      ["g v", "Review"],
      ["g p", "Subnets"],
      ["g s", "Scans"],
      ["g i", "Discovery inbox"],
      ["g c", "Changelog"],
      ["g r", "Racks"],
      ["g e", "Devices"],
      ["g m", "Monitoring"],
      ["g h", "Docs"],
    ],
  },
  {
    name: "Tables",
    items: [
      ["j / ↓", "Next row"],
      ["k / ↑", "Previous row"],
      ["Enter", "Open focused row"],
      ["Home / End", "First / last row"],
      ["Alt+↑ / Alt+↓", "Move focused row (orderable lists)"],
    ],
  },
  {
    name: "Subnet grid",
    items: [
      ["← ↑ ↓ →", "Move between addresses"],
      ["Enter", "Open address"],
      ["Drag", "Select a span of addresses"],
      ["Esc", "Clear span selection"],
    ],
  },
];

function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="rounded border bg-muted px-1.5 py-0.5 font-mono text-[11px]">
      {children}
    </kbd>
  );
}

export function ShortcutsOverlay({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (o: boolean) => void;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Keyboard shortcuts</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          {GROUPS.map((g) => (
            <div key={g.name}>
              <div className="mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
                {g.name}
              </div>
              <div className="space-y-1">
                {g.items.map(([keys, action]) => (
                  <div
                    key={keys}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="text-muted-foreground">{action}</span>
                    <span className="flex gap-1">
                      {keys.split(" ").map((k, i) => (
                        <Kbd key={i}>{k}</Kbd>
                      ))}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
          <p className="border-t pt-3 text-xs text-muted-foreground">
            Single-key shortcuts are inactive while typing in a field or while
            a dialog is open.
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
