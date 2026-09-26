"use client";

import Link from "next/link";

import { api } from "@/lib/api";
import { useAsyncData } from "@/lib/use-async-data";
import type { DocsPage } from "@/types";
import { PageEditor } from "@/components/docs/page-editor";

/** Edit wrapper — fetches the page by slug then hands it to PageEditor. */
export function PageEdit({ slug }: { slug: string }) {
  const pageQ = useAsyncData(
    () =>
      api.get<DocsPage>(
        `/api/v1/docs-pages/slug/${encodeURIComponent(slug)}`
      ),
    [slug]
  );

  if (pageQ.loading)
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  if (pageQ.error || !pageQ.data)
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
  return <PageEditor page={pageQ.data} />;
}
