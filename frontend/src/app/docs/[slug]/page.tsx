import { readFileSync } from "node:fs";
import path from "node:path";

import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArrowLeft, ArrowRight } from "lucide-react";

import {
  DOC_ARTICLES,
  docCategoryLabel,
  docHref,
  getDoc,
} from "@/lib/docs";
import { DocsContent } from "@/components/docs/docs-content";

// Articles are a fixed set — unknown slugs 404 rather than prerendering lazily.
export const dynamicParams = false;

export function generateStaticParams() {
  return DOC_ARTICLES.map((a) => ({ slug: a.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  return { title: getDoc(slug)?.title ?? "Docs" };
}

function loadMarkdown(slug: string): string | null {
  // slug is validated against the registry before this runs, so no traversal.
  try {
    return readFileSync(
      path.join(process.cwd(), "src/content/docs", `${slug}.md`),
      "utf8"
    );
  } catch {
    return null;
  }
}

export default async function DocPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const doc = getDoc(slug);
  if (!doc) notFound();
  const markdown = loadMarkdown(slug);
  if (markdown === null) notFound();

  const idx = DOC_ARTICLES.findIndex((a) => a.slug === slug);
  const prev = idx > 0 ? DOC_ARTICLES[idx - 1] : null;
  const next = idx < DOC_ARTICLES.length - 1 ? DOC_ARTICLES[idx + 1] : null;

  return (
    <article>
      <div className="mb-4 flex items-center gap-2 text-xs text-muted-foreground">
        <Link href="/docs" className="hover:text-foreground">
          Docs
        </Link>
        <span>/</span>
        <span className="uppercase tracking-wider">
          {docCategoryLabel(doc.category)}
        </span>
      </div>
      <DocsContent markdown={markdown} />
      <div className="mt-10 flex items-center justify-between border-t pt-4 text-sm">
        {prev ? (
          <Link
            href={docHref(prev.slug)}
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" /> {prev.title}
          </Link>
        ) : (
          <span />
        )}
        {next ? (
          <Link
            href={docHref(next.slug)}
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground"
          >
            {next.title} <ArrowRight className="h-4 w-4" />
          </Link>
        ) : (
          <span />
        )}
      </div>
    </article>
  );
}
