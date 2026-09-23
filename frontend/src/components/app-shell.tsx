"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  BookOpen,
  Building2,
  Cable,
  ChevronDown,
  Container,
  Cpu,
  FolderTree,
  HardDrive,
  History,
  Inbox,
  Keyboard,
  LayoutDashboard,
  ListOrdered,
  LogOut,
  Menu,
  Network,
  PanelLeftClose,
  PanelLeftOpen,
  Radar,
  ScanLine,
  Search,
  Server,
  Settings,
  ShieldCheck,
  Tags,
  Upload,
  Waypoints,
  Zap,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { AuthProvider, authCtxValue } from "@/lib/auth";
import { PERM, ROLE_META } from "@/lib/permissions";
import { usePrefs } from "@/lib/prefs";
import { useGlobalShortcuts } from "@/lib/shortcuts";
import type { AuthStatus } from "@/types";
import { Button } from "@/components/ui/button";
import { QuickScanDialog } from "@/components/quick-scan";
import { CommandPalette } from "@/components/command-palette";
import { ShortcutsOverlay } from "@/components/shortcuts-overlay";
import {
  Sheet,
  SheetContent,
  SheetTitle,
} from "@/components/ui/sheet";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface NavGroup {
  label: string | null;
  items: NavItem[];
}

const NAV_GROUPS: NavGroup[] = [
  {
    label: null,
    items: [{ href: "/", label: "Dashboard", icon: LayoutDashboard }],
  },
  {
    label: "IPAM",
    items: [
      { href: "/sites", label: "Sites", icon: Building2 },
      { href: "/vrfs", label: "VRFs", icon: Waypoints },
      { href: "/vlans", label: "VLANs", icon: Zap },
      { href: "/prefixes", label: "Subnets", icon: Network },
      { href: "/tree", label: "Hierarchy", icon: FolderTree },
    ],
  },
  {
    label: "Inventory",
    items: [
      { href: "/circuits", label: "Circuits", icon: Cable },
      { href: "/certificates", label: "Certificates", icon: ShieldCheck },
      { href: "/inventory", label: "Inventory", icon: HardDrive },
      { href: "/lists", label: "Lists", icon: ListOrdered },
      { href: "/racks", label: "Racks", icon: Container },
      { href: "/devices", label: "Devices", icon: Cpu },
      { href: "/services", label: "Services", icon: Server },
    ],
  },
  {
    label: "Operations",
    items: [
      { href: "/discovery", label: "Discovery Inbox", icon: Inbox },
      { href: "/scans", label: "Scans", icon: ScanLine },
      { href: "/import", label: "Import", icon: Upload },
      { href: "/changelog", label: "Changelog", icon: History },
    ],
  },
  {
    label: "System",
    items: [
      { href: "/tags", label: "Tags", icon: Tags },
      { href: "/docs", label: "Docs", icon: BookOpen },
      { href: "/settings", label: "Settings", icon: Settings },
    ],
  },
];

const NAV_FLAT = NAV_GROUPS.flatMap((g) => g.items);

const AUTH_ROUTES = ["/login", "/setup"];

const IS_MAC =
  typeof navigator !== "undefined" &&
  /Mac|iPhone|iPad/.test(navigator.platform);
const KBD_HINT = IS_MAC ? "⌘K" : "Ctrl K";

function isActive(href: string, pathname: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

function NavLink({
  item,
  pathname,
  collapsed,
  onNavigate,
}: {
  item: NavItem;
  pathname: string;
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const active = isActive(item.href, pathname);
  const link = (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-label={collapsed ? item.label : undefined}
      aria-current={active ? "page" : undefined}
      className={cn(
        "flex items-center rounded-md border-l-2 text-sm transition-colors",
        collapsed ? "justify-center p-2.5" : "gap-3 px-3 py-2",
        active
          ? "border-emerald-400 bg-emerald-500/10 font-semibold text-emerald-400"
          : "border-transparent text-muted-foreground hover:bg-accent hover:text-foreground"
      )}
    >
      <item.icon className="h-4 w-4 shrink-0" />
      {!collapsed && item.label}
    </Link>
  );
  if (!collapsed) return link;
  return (
    <Tooltip>
      <TooltipTrigger asChild>{link}</TooltipTrigger>
      <TooltipContent side="right">{item.label}</TooltipContent>
    </Tooltip>
  );
}

function NavItems({
  pathname,
  collapsed,
  groups,
  onToggleGroup,
  onNavigate,
}: {
  pathname: string;
  collapsed: boolean;
  groups: Record<string, boolean>;
  onToggleGroup: (label: string) => void;
  onNavigate?: () => void;
}) {
  // Icon-only rail: groups collapse away, everything flattens.
  if (collapsed) {
    return (
      <>
        {NAV_FLAT.map((item) => (
          <NavLink
            key={item.href}
            item={item}
            pathname={pathname}
            collapsed
            onNavigate={onNavigate}
          />
        ))}
      </>
    );
  }
  return (
    <>
      {NAV_GROUPS.map((group) => {
        if (group.label === null) {
          return group.items.map((item) => (
            <NavLink
              key={item.href}
              item={item}
              pathname={pathname}
              collapsed={false}
              onNavigate={onNavigate}
            />
          ));
        }
        const open = groups[group.label] !== false;
        return (
          <div key={group.label} className="pt-2">
            <button
              type="button"
              aria-expanded={open}
              onClick={() => onToggleGroup(group.label!)}
              className="flex w-full items-center justify-between rounded px-3 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70 hover:text-muted-foreground"
            >
              {group.label}
              <ChevronDown
                className={cn(
                  "h-3 w-3 transition-transform",
                  !open && "-rotate-90"
                )}
              />
            </button>
            {open &&
              group.items.map((item) => (
                <NavLink
                  key={item.href}
                  item={item}
                  pathname={pathname}
                  collapsed={false}
                  onNavigate={onNavigate}
                />
              ))}
          </div>
        );
      })}
    </>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [scanOpen, setScanOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [prefs, setPrefs] = usePrefs();
  const isAuthRoute = AUTH_ROUTES.includes(pathname);
  const collapsed = prefs.sidebarCollapsed;

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
      .catch(() =>
        setAuth({
          initialized: true,
          authenticated: true,
          allow_insecure: true,
          username: null,
          role: null,
          permissions: [],
        })
      );
  }, [isAuthRoute, router, pathname]);

  // Route changes close the mobile drawer.
  useEffect(() => setDrawerOpen(false), [pathname]);

  // ⌘K / Ctrl+K palette, "/" search, "?" overlay, g-chords, j/k row nav.
  const paletteToggle = useCallback(() => setPaletteOpen((v) => !v), []);
  const paletteOpenCb = useCallback(() => setPaletteOpen(true), []);
  const helpOpenCb = useCallback(() => setHelpOpen(true), []);
  useGlobalShortcuts({
    enabled: !isAuthRoute,
    onPaletteToggle: paletteToggle,
    onPaletteOpen: paletteOpenCb,
    onHelpOpen: helpOpenCb,
  });

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

  const ctx = authCtxValue(auth);
  const toggleGroup = (label: string) =>
    setPrefs({
      sidebarGroups: {
        ...prefs.sidebarGroups,
        [label]: prefs.sidebarGroups[label] === false,
      },
    });

  const brand = (
    <>
      <Network className="h-5 w-5 shrink-0 text-emerald-400" />
      <span className="text-base font-semibold tracking-tight">IpamBox</span>
    </>
  );

  return (
    <AuthProvider value={ctx}>
      <div className="flex min-h-screen">
      <aside
        className={cn(
          "fixed inset-y-0 z-30 hidden flex-col border-r bg-card transition-[width] md:flex print:hidden",
          collapsed ? "w-16" : "w-60"
        )}
      >
        <div
          className={cn(
            "flex h-14 items-center gap-2 border-b",
            collapsed ? "justify-center px-0" : "px-5"
          )}
        >
          {collapsed ? (
            <Network className="h-5 w-5 text-emerald-400" />
          ) : (
            brand
          )}
        </div>
        <nav
          className={cn(
            "flex-1 space-y-1 overflow-y-auto",
            collapsed ? "p-2" : "p-3"
          )}
        >
          <NavItems
            pathname={pathname}
            collapsed={collapsed}
            groups={prefs.sidebarGroups}
            onToggleGroup={toggleGroup}
          />
        </nav>
        <div
          className={cn(
            "flex items-center border-t p-3 text-xs text-muted-foreground",
            collapsed ? "flex-col gap-1" : "justify-between"
          )}
        >
          {!collapsed && (
            <span className="min-w-0 truncate">
              {auth.username
                ? `Signed in as ${auth.username}`
                : "IPAM & network scanner"}
              {auth.role && (
                <span className="ml-1 text-muted-foreground/70">
                  · {ROLE_META[auth.role].tier}
                </span>
              )}
            </span>
          )}
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
              onClick={() => setPrefs({ sidebarCollapsed: !collapsed })}
            >
              {collapsed ? (
                <PanelLeftOpen className="h-3.5 w-3.5" />
              ) : (
                <PanelLeftClose className="h-3.5 w-3.5" />
              )}
            </Button>
            {!auth.allow_insecure && (
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7"
                aria-label="Sign out"
                title="Sign out"
                onClick={signOut}
              >
                <LogOut className="h-3.5 w-3.5" />
              </Button>
            )}
          </div>
        </div>
      </aside>

      <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
        <SheetContent side="left" className="w-72 max-w-[85vw] p-0">
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <div className="flex h-14 items-center gap-2 border-b px-5">
            {brand}
          </div>
          <div className="border-b p-3">
            <Button
              variant="outline"
              className="w-full justify-start gap-2 text-muted-foreground"
              onClick={() => {
                setDrawerOpen(false);
                setPaletteOpen(true);
              }}
            >
              <Search className="h-4 w-4" /> Search
            </Button>
          </div>
          <nav className="space-y-1 p-3">
            <NavItems
              pathname={pathname}
              collapsed={false}
              groups={prefs.sidebarGroups}
              onToggleGroup={toggleGroup}
              onNavigate={() => setDrawerOpen(false)}
            />
          </nav>
        </SheetContent>
      </Sheet>

      <div
        className={cn(
          "flex min-h-screen min-w-0 flex-1 flex-col transition-[margin] print:ml-0",
          collapsed ? "md:ml-16" : "md:ml-60"
        )}
      >
        <header className="sticky top-0 z-20 flex h-14 items-center justify-between gap-2 border-b bg-background/80 px-4 backdrop-blur md:px-6 print:hidden">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              aria-label="Open navigation"
              onClick={() => setDrawerOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <span className="text-sm font-semibold tracking-tight md:hidden">
              IpamBox
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              aria-label="Search"
              className="gap-2 text-muted-foreground"
              onClick={() => setPaletteOpen(true)}
            >
              <Search className="h-4 w-4" />
              <span className="hidden sm:inline">Search</span>
              <kbd className="hidden rounded border px-1 text-[10px] sm:inline">
                {KBD_HINT}
              </kbd>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              aria-label="Keyboard shortcuts"
              title="Keyboard shortcuts (?)"
              onClick={() => setHelpOpen(true)}
            >
              <Keyboard className="h-4 w-4" />
            </Button>
            {ctx.can(PERM.DATA_WRITE) && (
              <Button size="sm" onClick={() => setScanOpen(true)}>
                <Radar /> Quick scan
              </Button>
            )}
          </div>
        </header>
        <main className="min-w-0 flex-1 p-4 md:p-6">{children}</main>
      </div>

      <QuickScanDialog
        open={scanOpen}
        onOpenChange={setScanOpen}
        onFinished={() => window.dispatchEvent(new Event("ipam:refresh"))}
      />
      <CommandPalette open={paletteOpen} onOpenChange={setPaletteOpen} />
      <ShortcutsOverlay open={helpOpen} onOpenChange={setHelpOpen} />
      </div>
    </AuthProvider>
  );
}
