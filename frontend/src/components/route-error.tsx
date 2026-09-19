"use client";

import { useEffect } from "react";
import { TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

/** Shared body for every route-segment error.tsx boundary. */
export default function RouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[40vh] items-center justify-center">
      <Card className="w-full max-w-md">
        <CardContent className="flex flex-col items-center gap-3 py-8 text-center">
          <TriangleAlert className="h-8 w-8 text-amber-400" />
          <h2 className="text-lg font-semibold">Something went wrong</h2>
          <p className="break-all text-sm text-muted-foreground">
            {error.message || "An unexpected error occurred."}
          </p>
          <Button size="sm" variant="outline" onClick={reset}>
            Try again
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
