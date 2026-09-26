"use client";

import Link from "next/link";
import { useState } from "react";
import { FileText, Pencil, Plus, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import { useAsyncData } from "@/lib/use-async-data";
import { pageHref } from "@/lib/docs";
import type { DocsPage, Page } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

/**
 * The "Pages" section of /docs — user-authored markdown pages, visually
 * separated from the builtin help above. Listed latest-first; write
 * actions are gated on DATA_WRITE / DATA_DELETE.
 */
export function PagesSection({ filter }: { filter: string }) {
  const { can } = useAuth();
  const canWrite = can(PERM.DATA_WRITE);
  const canDelete = can(PERM.DATA_DELETE);
  const pagesQ = useAsyncData(
    () => api.get<Page<DocsPage>>("/api/v1/docs-pages?limit=500"),
    []
  );
  const [deleting, setDeleting] = useState<DocsPage | null>(null);
  const [busy, setBusy] = useState(false);

  const needle = filter.trim().toLowerCase();
  const pages = (pagesQ.data?.items ?? [])
    .filter(
      (p) =>
        !needle ||
        p.title.toLowerCase().includes(needle) ||
        p.category.toLowerCase().includes(needle)
    )
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at));

  const doDelete = async () => {
    if (!deleting) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/docs-pages/${deleting.id}`);
      toast.success(`Deleted “${deleting.title}”`);
      setDeleting(null);
      void pagesQ.reload();
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="border-t pt-4">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
          Pages — your runbooks & notes
        </h2>
        {canWrite && (
          <Button size="sm" variant="outline" asChild className="h-7 gap-1.5 px-2.5 text-xs">
            <Link href="/docs/pages/new">
              <Plus className="h-3.5 w-3.5" /> New page
            </Link>
          </Button>
        )}
      </div>

      {pagesQ.loading ? (
        <p className="text-sm text-muted-foreground">Loading pages…</p>
      ) : pagesQ.error ? (
        <p className="text-sm text-rose-400">{pagesQ.error}</p>
      ) : pages.length === 0 ? (
        <p className="py-2 text-sm text-muted-foreground">
          {needle
            ? `No pages match “${filter.trim()}”.`
            : canWrite
              ? "No pages yet — write your first runbook."
              : "No pages yet."}
        </p>
      ) : (
        <div className="grid gap-2 sm:grid-cols-2">
          {pages.map((p) => (
            <div
              key={p.id}
              className="group flex items-start gap-3 rounded-lg border border-dashed p-3 transition-colors hover:border-emerald-500/40 hover:bg-accent"
            >
              <FileText className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
              <span className="min-w-0 flex-1">
                <Link
                  href={pageHref(p.slug)}
                  dir="auto"
                  className="block truncate text-sm font-medium hover:underline"
                >
                  {p.title}
                </Link>
                <span className="block text-xs text-muted-foreground">
                  {p.category} · {p.created_by ?? "?"} · {fmtTs(p.updated_at)}
                </span>
              </span>
              {canWrite && (
                <Link
                  href={`${pageHref(p.slug)}/edit`}
                  aria-label={`Edit ${p.title}`}
                  className="rounded p-1 text-muted-foreground hover:text-foreground"
                >
                  <Pencil className="h-3.5 w-3.5" />
                </Link>
              )}
              {canDelete && (
                <button
                  type="button"
                  aria-label={`Delete ${p.title}`}
                  onClick={() => setDeleting(p)}
                  className="rounded p-1 text-muted-foreground hover:text-rose-400"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      <Dialog
        open={deleting !== null}
        onOpenChange={(o) => !o && setDeleting(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete page</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {deleting?.title}
            </span>
            ? Links to /docs/pages/{deleting?.slug} will stop working.
          </p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleting(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete} disabled={busy}>
              {busy ? "Deleting…" : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}
