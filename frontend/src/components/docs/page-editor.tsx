"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/api";
import type { DocsPage } from "@/types";
import { Button } from "@/components/ui/button";
import { Input, Textarea } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DocsContent } from "@/components/docs/docs-content";

/** Mirror of the backend's slugify (NFKC + lowercase + [^\w]+ → "-") so the
 *  suggestion matches what the server would pick; the server still owns the
 *  real slug and appends -2 on collision. */
export function suggestSlug(title: string): string {
  const slug = title
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\p{M}_]+/gu, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "page";
}

/**
 * Side-by-side markdown editor for user Pages — textarea on the left, the
 * same DocsContent renderer (react-markdown + GFM, no raw HTML) on the
 * right. Slug auto-suggests from the title until the user edits it.
 */
export function PageEditor({ page }: { page: DocsPage | null }) {
  const router = useRouter();
  const editing = page !== null;
  const [title, setTitle] = useState(page?.title ?? "");
  const [slug, setSlug] = useState(page?.slug ?? "");
  const [slugTouched, setSlugTouched] = useState(editing);
  const [category, setCategory] = useState(page?.category ?? "notes");
  const [body, setBody] = useState(page?.body ?? "");
  const [busy, setBusy] = useState(false);

  const suggested = suggestSlug(title);
  useEffect(() => {
    if (!slugTouched) setSlug(suggested);
  }, [suggested, slugTouched]);

  const save = async () => {
    if (!title.trim()) {
      toast.error("Title is required");
      return;
    }
    setBusy(true);
    try {
      const payload = {
        title: title.trim(),
        slug: slug.trim() || undefined,
        category: category.trim() || "notes",
        body,
      };
      const saved = editing
        ? await api.patch<DocsPage>(`/api/v1/docs-pages/${page.id}`, payload)
        : await api.post<DocsPage>("/api/v1/docs-pages", payload);
      toast.success(editing ? "Page saved" : "Page created");
      router.push(`/docs/pages/${saved.slug}`);
    } catch (e) {
      toast.error("Save failed", { description: String(e) });
    } finally {
      setBusy(false);
    }
  };

  const back = editing ? `/docs/pages/${page.slug}` : "/docs";

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-2">
        <Link
          href={back}
          className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> {editing ? "Back to page" : "Docs"}
        </Link>
        <Button size="sm" onClick={save} disabled={busy || !title.trim()}>
          {busy ? "Saving…" : editing ? "Save" : "Create page"}
        </Button>
      </div>

      <div className="grid gap-3 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
        <div className="space-y-1">
          <Label htmlFor="page-title">Title</Label>
          <Input
            id="page-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Switch failover runbook"
            dir="auto"
            autoFocus={!editing}
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="page-slug">Slug</Label>
          <Input
            id="page-slug"
            value={slug}
            onChange={(e) => {
              setSlugTouched(true);
              setSlug(e.target.value);
            }}
            placeholder={suggested}
            dir="ltr"
            className="font-mono text-xs"
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="page-category">Category</Label>
          <Input
            id="page-category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="notes"
            dir="ltr"
            className="w-32"
            list="page-categories"
          />
          <datalist id="page-categories">
            <option value="notes" />
            <option value="runbook" />
            <option value="procedure" />
          </datalist>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-1">
          <Label htmlFor="page-body">Markdown</Label>
          <Textarea
            id="page-body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder={"## Steps\n\n1. …"}
            dir="auto"
            className="min-h-[55vh] font-mono text-xs leading-5"
          />
        </div>
        <div className="space-y-1">
          <Label>Preview</Label>
          <div className="min-h-[55vh] rounded-md border bg-card p-4">
            {body.trim() ? (
              <DocsContent markdown={body} />
            ) : (
              <p className="text-sm text-muted-foreground">
                Preview appears here — GFM markdown, no raw HTML.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
