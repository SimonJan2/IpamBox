"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ArrowLeft, Pencil, Trash2 } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PERM } from "@/lib/permissions";
import { fmtTs } from "@/lib/prefs";
import { useAsyncData } from "@/lib/use-async-data";
import type { DocsPage } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { DocsContent } from "@/components/docs/docs-content";

/** Render a user page fetched by slug (/docs/pages/<slug>). Builtin help
 *  lives at /docs/<slug> — this is the user workspace, kept distinct. */
export function PageView({ slug }: { slug: string }) {
  const router = useRouter();
  const { can } = useAuth();
  const pageQ = useAsyncData(
    () =>
      api.get<DocsPage>(
        `/api/v1/docs-pages/slug/${encodeURIComponent(slug)}`
      ),
    [slug]
  );
  const [deleting, setDeleting] = useState(false);
  const [busy, setBusy] = useState(false);
  const page = pageQ.data;

  const doDelete = async () => {
    if (!page) return;
    setBusy(true);
    try {
      await api.del(`/api/v1/docs-pages/${page.id}`);
      toast.success(`Deleted “${page.title}”`);
      router.push("/docs");
    } catch (e) {
      toast.error("Delete failed", { description: String(e) });
      setBusy(false);
      setDeleting(false);
    }
  };

  if (pageQ.loading)
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (pageQ.error || !page)
    return (
      <div className="space-y-3">
        <p className="text-sm text-muted-foreground">
          This page doesn't exist (or was deleted).
        </p>
        <Link href="/docs" className="text-sm text-emerald-400 hover:underline">
          ← Back to docs
        </Link>
      </div>
    );

  return (
    <article>
      <div className="mb-4 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Link href="/docs" className="hover:text-foreground">
            Docs
          </Link>
          <span>/</span>
          <span className="uppercase tracking-wider">Pages</span>
          <span>/</span>
          <span dir="auto">{page.category}</span>
        </div>
        {(can(PERM.DATA_WRITE) || can(PERM.DATA_DELETE)) && (
          <div className="flex gap-1">
            {can(PERM.DATA_WRITE) && (
              <Button variant="ghost" size="sm" asChild className="h-7 px-2 text-xs">
                <Link href={`/docs/pages/${page.slug}/edit`}>
                  <Pencil className="mr-1 h-3.5 w-3.5" /> Edit
                </Link>
              </Button>
            )}
            {can(PERM.DATA_DELETE) && (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 px-2 text-xs"
                onClick={() => setDeleting(true)}
              >
                <Trash2 className="mr-1 h-3.5 w-3.5 text-rose-400" /> Delete
              </Button>
            )}
          </div>
        )}
      </div>
      <h1 dir="auto" className="mb-1 text-2xl font-semibold tracking-tight">
        {page.title}
      </h1>
      <p className="mb-6 text-xs text-muted-foreground">
        {page.created_by ?? "?"} · created {fmtTs(page.created_at)} · updated{" "}
        {fmtTs(page.updated_at)}
      </p>
      {page.body.trim() ? (
        <DocsContent markdown={page.body} />
      ) : (
        <p className="text-sm text-muted-foreground">This page is empty.</p>
      )}

      <Dialog open={deleting} onOpenChange={setDeleting}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete page</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Delete{" "}
            <span dir="auto" className="font-medium text-foreground">
              {page.title}
            </span>
            ? This cannot be undone.
          </p>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleting(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={doDelete} disabled={busy}>
              {busy ? "Deleting…" : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </article>
  );
}
