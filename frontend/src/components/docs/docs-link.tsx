import Link from "next/link";
import { CircleHelp } from "lucide-react";

import { cn } from "@/lib/utils";
import { docHref, getDoc } from "@/lib/docs";
import { Button } from "@/components/ui/button";

/**
 * Small "?" affordance placed next to a page's <h1> that jumps to the matching
 * docs article. Unknown slugs render nothing so a stale link never ships a 404.
 */
export function DocsLink({
  slug,
  className,
}: {
  slug: string;
  className?: string;
}) {
  const doc = getDoc(slug);
  if (!doc) return null;
  const label = `Docs: ${doc.title}`;
  return (
    <Button
      variant="ghost"
      size="icon"
      asChild
      className={cn("h-7 w-7 text-muted-foreground", className)}
    >
      <Link href={docHref(doc.slug)} title={label} aria-label={label}>
        <CircleHelp className="h-4 w-4" />
      </Link>
    </Button>
  );
}
