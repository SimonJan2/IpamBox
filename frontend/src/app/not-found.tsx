import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-3 text-center">
      <p className="font-mono text-4xl font-semibold text-emerald-400">404</p>
      <p className="text-sm text-muted-foreground">
        This page doesn&apos;t exist or the object was deleted.
      </p>
      <Button variant="outline" size="sm" asChild>
        <Link href="/">Back to dashboard</Link>
      </Button>
    </div>
  );
}
