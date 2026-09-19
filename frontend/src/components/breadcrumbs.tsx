"use client";

import Link from "next/link";
import { Fragment, useEffect, useMemo, useState } from "react";
import { ChevronRight } from "lucide-react";

import { api } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { PrefixNode, SiteNode } from "@/types";
import { Skeleton } from "@/components/ui/separator";

export interface Crumb {
  label: React.ReactNode;
  href?: string;
  mono?: boolean;
}

export function Breadcrumbs({ items }: { items: Crumb[] }) {
  return (
    <nav
      aria-label="Breadcrumb"
      className="flex min-w-0 items-center gap-1 text-sm text-muted-foreground"
    >
      {items.map((c, i) => (
        <Fragment key={i}>
          {i > 0 && (
            <ChevronRight className="h-3.5 w-3.5 shrink-0 opacity-50" />
          )}
          {c.href ? (
            <Link
              href={c.href}
              className="truncate transition-colors hover:text-foreground"
            >
              <span dir="auto" className={cn(c.mono && "font-mono")}>
                {c.label}
              </span>
            </Link>
          ) : (
            <span
              dir="auto"
              className={cn("truncate text-foreground", c.mono && "font-mono")}
            >
              {c.label}
            </span>
          )}
        </Fragment>
      ))}
    </nav>
  );
}

/** Walk the Site -> VRF -> prefix tree and return the chain down to
 * `prefixId` (inclusive), or null while loading / when not found. */
function findChain(tree: SiteNode[] | null, prefixId: number): Crumb[] | null {
  if (!tree) return null;
  for (const site of tree) {
    for (const vrf of site.vrfs) {
      const walk = (n: PrefixNode, path: Crumb[]): Crumb[] | null => {
        const next: Crumb[] = [
          ...path,
          { label: n.prefix, href: `/prefixes/${n.id}`, mono: true },
        ];
        if (n.id === prefixId) return next;
        for (const c of n.children) {
          const hit = walk(c, next);
          if (hit) return hit;
        }
        return null;
      };
      for (const p of vrf.prefixes) {
        const chain = walk(p, [
          { label: site.name, href: "/sites" },
          { label: vrf.name, href: `/prefixes?vrf=${vrf.id}` },
        ]);
        if (chain) {
          // The last crumb is the current page — unlinked.
          chain[chain.length - 1] = {
            ...chain[chain.length - 1],
            href: undefined,
          };
          return chain;
        }
      }
    }
  }
  return null;
}

export function PrefixBreadcrumbs({ prefixId }: { prefixId: number }) {
  const [tree, setTree] = useState<SiteNode[] | null>(null);

  useEffect(() => {
    api
      .get<SiteNode[]>("/api/v1/prefixes/tree")
      .then(setTree)
      .catch(() => {});
  }, []);

  const chain = useMemo(() => findChain(tree, prefixId), [tree, prefixId]);

  if (tree === null) return <Skeleton className="h-5 w-72" />;
  if (!chain) return null;
  return <Breadcrumbs items={chain} />;
}
