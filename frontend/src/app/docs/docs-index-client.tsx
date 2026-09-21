"use client";

import Link from "next/link";
import { useState } from "react";
import { Search } from "lucide-react";

import {
  DOC_ARTICLES,
  DOC_CATEGORIES,
  docHref,
  searchDocs,
} from "@/lib/docs";
import { Input } from "@/components/ui/input";

export default function DocsIndexClient() {
  const [q, setQ] = useState("");
  const filtering = q.trim().length > 0;
  const articles = filtering ? searchDocs(q) : DOC_ARTICLES;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-semibold">Documentation</h1>
        <p className="text-sm text-muted-foreground">
          Guides for every feature in IpamBox. Pick a topic on the left, or
          filter below.
        </p>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Filter guides…"
          aria-label="Filter guides"
          className="pl-8"
        />
      </div>

      {articles.length === 0 ? (
        <p className="py-8 text-sm text-muted-foreground">
          No guides match “{q.trim()}”.
        </p>
      ) : (
        DOC_CATEGORIES.map((cat) => {
          const rows = articles.filter((a) => a.category === cat.key);
          if (!rows.length) return null;
          return (
            <div key={cat.key}>
              <h2 className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
                {cat.label}
              </h2>
              <div className="grid gap-2 sm:grid-cols-2">
                {rows.map((a) => (
                  <Link
                    key={a.slug}
                    href={docHref(a.slug)}
                    className="flex items-start gap-3 rounded-lg border p-3 transition-colors hover:border-emerald-500/40 hover:bg-accent"
                  >
                    <a.icon className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400" />
                    <span className="min-w-0">
                      <span className="block text-sm font-medium">
                        {a.title}
                      </span>
                      <span className="block text-xs text-muted-foreground">
                        {a.description}
                      </span>
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
