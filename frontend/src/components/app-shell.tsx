"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  Building2,
  FolderTree,
  History,
  Inbox,
  LayoutDashboard,
  LogOut,
  Network,
  Radar,
  ScanLine,
  Tags,
  Waypoints,
  Zap,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import type { AuthStatus } from "@/types";
import { Button } from "@/components/ui/button";
import { QuickScanDialog } from "@/components/quick-scan";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/sites", label: "Sites", icon: Building2 },
  { href: "/vrfs", label: "VRFs", icon: Waypoints },
  { href: "/vlans", label: "VLANs", icon: Zap },
  { href: "/prefixes", label: "Subnets", icon: Network },
  { href: "/tree", label: "Hierarchy", icon: FolderTree },
  { href: "/discovery", label: "Discovery Inbox", icon: Inbox },
  { href: "/scans", label: "Scans", icon: ScanLine },
  { href: "/tags", label: "Tags", icon: Tags },
  { href: "/changelog", label: "Changelog", icon: History },
];

const AUTH_ROUTES = ["/login", "/setup"];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [scanOpen, setScanOpen] = useState(false);
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const isAuthRoute = AUTH_ROUTES.includes(pathname);

  useEffect(() => {
    if (isAuthRoute) return;
    api
      .get<AuthStatus>("/api/v1/auth/status")
      .then((s) => {
        if (!s.allow_insecure && !s.initialized) {
          router.replace("/setup");
          return;
        }
        if (!s.allow_insecure && !s.authenticated) {
          router.replace("/login");
          return;
        }
        setAuth(s);
      })
      .catch(() => setAuth({ initialized: true, authenticated: true, allow_insecure: true, username: null }));
  }, [isAuthRoute, router, pathname]);

  const signOut = async () => {
    try {
      await api.post("/api/v1/auth/logout");
    } finally {
      window.location.assign("/login");
    }
  };

  if (isAuthRoute) {
    return <div className="min-h-screen">{children}</div>;
  }

  if (auth === null) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Network className="h-6 w-6 animate-pulse text-emerald-400" />
      </div>
    );
  }

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
        <div className="flex items-center justify-between border-t p-3 text-xs text-muted-foreground">
          <span>{auth.username ? `Signed in as ${auth.username}` : "IPAM & network scanner"}</span>
          {!auth.allow_insecure && (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              title="Sign out"
              onClick={signOut}
            >
              <LogOut className="h-3.5 w-3.5" />
            </Button>
          )}
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
