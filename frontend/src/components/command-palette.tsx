"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  BookOpen,
  Building2,
  Cable,
  Crosshair,
  Globe,
  HardDrive,
  History,
  ListOrdered,
  Network,
  Search,
  Server,
  ShieldCheck,
  Waypoints,
  Zap,
} from "lucide-react";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import { docCategoryLabel, docHref, searchDocs } from "@/lib/docs";
import { getPrefs, savePrefs } from "@/lib/prefs";
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@/components/ui/dialog";

interface SearchOut {
  addresses: {
    id: number;
    address: string;
    hostname: string | null;
    prefix_id: number;
    status: string;
  }[];
  prefixes: {
    id: number;
    prefix: string;
    description: string | null;
  }[];
  sites: { id: number; name: string; code: string | null }[];
  vrfs: { id: number; name: string; rd: string | null }[];
  vlans: { id: number; vid: number; name: string }[];
  circuits: {
    id: number;
    site_name: string | null;
    site_code: string | null;
    bezeq_circuit_id: string | null;
    app_client_name: string | null;
  }[];
  certificates: {
    id: number;
    cert_name: string | null;
    server_name: string | null;
    platform: string | null;
  }[];
  assets: {
    id: number;
    vendor: string | null;
    model: string | null;
    serial_number: string | null;
    category: string | null;
  }[];
  services: {
    id: number;
    name: string | null;
    beneficiary: string | null;
    site_code: string | null;
  }[];
  lists: {
    id: number;
    name: string;
    slug: string;
    description: string | null;
  }[];
  list_rows: {
    id: number;
    list_id: number;
    list_slug: string;
    list_name: string;
    label: string;
  }[];
  jump: {
    address: string;
    prefix_id: number;
    prefix: string;
    exists: boolean;
  } | null;
}

type Icon = React.ComponentType<{ className?: string }>;

interface Item {
  group: string;
  icon: Icon;
  label: string;
  sub?: string;
  href: string;
}

const ENC = encodeURIComponent;

function itemsFor(res: SearchOut, q: string): Item[] {
  const items: Item[] = [];
  if (res.jump) {
    const j = res.jump;
    items.push({
      group: "Jump",
      icon: Crosshair,
      label: j.address,
      sub: j.exists ? `in ${j.prefix}` : `free in ${j.prefix}`,
      href: `/prefixes/${j.prefix_id}?q=${ENC(j.address)}`,
    });
  }
  for (const a of res.addresses)
    items.push({
      group: "Addresses",
      icon: Globe,
      label: a.address,
      sub: a.hostname ?? undefined,
      href: `/prefixes/${a.prefix_id}?q=${ENC(a.address)}`,
    });
  for (const p of res.prefixes)
    items.push({
      group: "Subnets",
      icon: Network,
      label: p.prefix,
      sub: p.description ?? undefined,
      href: `/prefixes/${p.id}`,
    });
  for (const s of res.sites)
    items.push({
      group: "Sites",
      icon: Building2,
      label: s.name,
      sub: s.code ?? undefined,
      href: `/sites?q=${ENC(q)}`,
    });
  for (const v of res.vrfs)
    items.push({
      group: "VRFs",
      icon: Waypoints,
      label: v.name,
      sub: v.rd ?? undefined,
      href: `/vrfs?q=${ENC(q)}`,
    });
  for (const v of res.vlans)
    items.push({
      group: "VLANs",
      icon: Zap,
      label: `${v.vid} · ${v.name}`,
      href: `/vlans?q=${ENC(q)}`,
    });
  for (const c of res.circuits)
    items.push({
      group: "Circuits",
      icon: Cable,
      label: c.bezeq_circuit_id ?? c.site_name ?? `#${c.id}`,
      sub: c.app_client_name ?? c.site_name ?? undefined,
      href: `/circuits?q=${ENC(q)}`,
    });
  for (const c of res.certificates)
    items.push({
      group: "Certificates",
      icon: ShieldCheck,
      label: c.cert_name ?? c.server_name ?? `#${c.id}`,
      sub: c.platform ?? undefined,
      href: `/certificates?q=${ENC(q)}`,
    });
  for (const a of res.assets)
    items.push({
      group: "Inventory",
      icon: HardDrive,
      label: [a.vendor, a.model].filter(Boolean).join(" ") || `#${a.id}`,
      sub: a.serial_number ?? a.category ?? undefined,
      href: `/inventory?q=${ENC(q)}`,
    });
  for (const s of res.services)
    items.push({
      group: "Services",
      icon: Server,
      label: s.name ?? `#${s.id}`,
      sub: s.beneficiary ?? s.site_code ?? undefined,
      href: `/services?q=${ENC(q)}`,
    });
  for (const l of res.lists ?? [])
    items.push({
      group: "Lists",
      icon: ListOrdered,
      label: l.name,
      sub: l.description ?? undefined,
      href: `/lists/${l.slug}`,
    });
  for (const r of res.list_rows ?? [])
    items.push({
      group: "Lists",
      icon: ListOrdered,
      label: r.label,
      sub: r.list_name,
      href: `/lists/${r.list_slug}?q=${ENC(r.label)}`,
    });
  return items;
}

function remember(item: Item) {
  const prev = getPrefs().searchRecent.filter((r) => r.href !== item.href);
  savePrefs({
    searchRecent: [{ label: item.label, href: item.href }, ...prev].slice(0, 5),
  });
}

export function CommandPalette({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Item[]>([]);
  const [searching, setSearching] = useState(false);
  const [active, setActive] = useState(0);
  const [recent, setRecent] = useState<{ label: string; href: string }[]>([]);
  const listRef = useRef<HTMLDivElement>(null);
  const seq = useRef(0);

  // Fresh state each open; recents read once mounted.
  useEffect(() => {
    if (open) {
      setQ("");
      setItems([]);
      setActive(0);
      setRecent(getPrefs().searchRecent);
    }
  }, [open]);

  // Debounced query (~200ms), stale responses discarded.
  useEffect(() => {
    if (!open) return;
    const query = q.trim();
    if (!query) {
      setItems([]);
      setSearching(false);
      return;
    }
    setSearching(true);
    const mySeq = ++seq.current;
    const t = setTimeout(() => {
      api
        .get<SearchOut>(`/api/v1/search?q=${ENC(query)}`)
        .then((res) => {
          if (seq.current !== mySeq) return;
          setItems(itemsFor(res, query));
          setSearching(false);
        })
        .catch(() => {
          if (seq.current !== mySeq) return;
          setItems([]);
          setSearching(false);
        });
    }, 200);
    return () => clearTimeout(t);
  }, [q, open]);

  useEffect(() => {
    setActive(0);
    listRef.current?.scrollTo({ top: 0 });
  }, [items]);

  const shown = useMemo<Item[]>(() => {
    if (!q.trim()) {
      return recent.map((r) => ({
        group: "Recent",
        icon: History,
        label: r.label,
        href: r.href,
      }));
    }
    // Doc guides are static — matched client-side, appended after data hits.
    const docItems = searchDocs(q)
      .slice(0, 6)
      .map<Item>((d) => ({
        group: "Docs",
        icon: BookOpen,
        label: d.title,
        sub: docCategoryLabel(d.category),
        href: docHref(d.slug),
      }));
    return [...items, ...docItems];
  }, [q, items, recent]);

  const pick = (item: Item) => {
    remember(item);
    onOpenChange(false);
    router.push(item.href);
  };

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!shown.length) return;
      const dir = e.key === "ArrowDown" ? 1 : -1;
      setActive((a) => (a + dir + shown.length) % shown.length);
      listRef.current
        ?.querySelectorAll("[data-item]")
        [(active + dir + shown.length) % shown.length]?.scrollIntoView({
          block: "nearest",
        });
    } else if (e.key === "Enter") {
      e.preventDefault();
      const item = shown[active];
      if (item) pick(item);
    }
  };

  let lastGroup = "";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="top-[12%] translate-y-0 gap-0 overflow-hidden p-0 sm:max-w-xl"
        onKeyDown={onKeyDown}
      >
        <DialogTitle className="sr-only">Search</DialogTitle>
        <div className="flex items-center gap-2 border-b px-4">
          <Search className="h-4 w-4 shrink-0 text-muted-foreground" />
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search addresses, sites, subnets…"
            aria-label="Search"
            className="h-12 w-full bg-transparent pr-8 text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>
        <div ref={listRef} className="max-h-80 overflow-y-auto p-2">
          {shown.length === 0 ? (
            <p className="px-3 py-8 text-center text-sm text-muted-foreground">
              {searching
                ? "Searching…"
                : q.trim()
                  ? `No results for “${q.trim()}”`
                  : "Type to search, or paste an IP address to jump to it."}
            </p>
          ) : (
            shown.map((item, i) => {
              const header =
                item.group !== lastGroup ? (
                  <div className="px-3 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
                    {(lastGroup = item.group)}
                  </div>
                ) : null;
              return (
                <div key={`${item.href}-${i}`}>
                  {header}
                  <button
                    type="button"
                    data-item
                    onMouseEnter={() => setActive(i)}
                    onClick={() => pick(item)}
                    className={cn(
                      "flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm",
                      i === active
                        ? "bg-accent text-foreground"
                        : "text-muted-foreground"
                    )}
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    <span dir="auto" className="min-w-0 flex-1 truncate">
                      {item.label}
                    </span>
                    {item.sub && (
                      <span
                        dir="auto"
                        className="max-w-[40%] truncate text-xs text-muted-foreground/70"
                      >
                        {item.sub}
                      </span>
                    )}
                  </button>
                </div>
              );
            })
          )}
        </div>
        <div className="flex items-center gap-3 border-t px-4 py-2 text-[11px] text-muted-foreground">
          <span>
            <kbd className="rounded border px-1">↑↓</kbd> navigate
          </span>
          <span>
            <kbd className="rounded border px-1">↵</kbd> open
          </span>
          <span>
            <kbd className="rounded border px-1">esc</kbd> close
          </span>
        </div>
      </DialogContent>
    </Dialog>
  );
}
