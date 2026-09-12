"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Building2,
  FolderTree,
  Inbox,
  LayoutDashboard,
  Network,
  Radar,
  ScanLine,
  Waypoints,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { QuickScanDialog } from "@/components/quick-scan";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/sites", label: "Sites", icon: Building2 },
  { href: "/vrfs", label: "VRFs", icon: Waypoints },
  { href: "/prefixes", label: "Subnets", icon: Network },
  { href: "/tree", label: "Hierarchy", icon: FolderTree },
  { href: "/discovery", label: "Discovery Inbox", icon: Inbox },
  { href: "/scans", label: "Scans", icon: ScanLine },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [scanOpen, setScanOpen] = useState(false);

  return (
    <div className="flex min-h-screen">
      <aside className="fixed inset-y-0 z-30 flex w-60 flex-col border-r bg-card">
        <div className="flex h-14 items-center gap-2 border-b px-5">
          <Network className="h-5 w-5 text-emerald-400" />
          <span className="text-base font-semibold tracking-tight">IpamBox</span>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {NAV.map((item) => {
            const active =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-emerald-500/10 text-emerald-400"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                )}
              >
                <item.icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t p-3 text-xs text-muted-foreground">
          IPAM &amp; network scanner
        </div>
      </aside>

      <div className="ml-60 flex min-h-screen flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b bg-background/80 px-6 backdrop-blur">
          <div />
          <Button size="sm" onClick={() => setScanOpen(true)}>
            <Radar /> Quick scan
          </Button>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>

      <QuickScanDialog
        open={scanOpen}
        onOpenChange={setScanOpen}
        onFinished={() => window.dispatchEvent(new Event("ipam:refresh"))}
      />
    </div>
  );
}
