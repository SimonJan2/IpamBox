"use client";

import { AlertTriangle, RotateCcw } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/separator";

/**
 * Uniform loading / error / empty wrapper around fetched data:
 * skeleton while loading, an inline error + retry on failure, a helpful
 * empty message, otherwise children.
 */
export function AsyncPanel({
  loading,
  error,
  empty = false,
  onRetry,
  emptyMessage = "Nothing here yet.",
  errorTitle = "Couldn't load data",
  skeleton,
  className,
  children,
}: {
  loading: boolean;
  error?: string | null;
  empty?: boolean;
  onRetry?: () => void;
  emptyMessage?: React.ReactNode;
  errorTitle?: string;
  skeleton?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}) {
  if (loading) {
    return <>{skeleton ?? <Skeleton className={cn("h-32 w-full", className)} />}</>;
  }
  if (error) {
    return (
      <div
        className={cn(
          "flex flex-col items-center gap-3 rounded-lg border border-rose-500/20 px-4 py-10 text-center",
          className
        )}
      >
        <AlertTriangle className="h-5 w-5 text-rose-400" />
        <div className="space-y-1">
          <p className="text-sm font-medium">{errorTitle}</p>
          <p className="text-xs text-muted-foreground">{error}</p>
        </div>
        {onRetry && (
          <Button size="sm" variant="outline" onClick={onRetry}>
            <RotateCcw /> Retry
          </Button>
        )}
      </div>
    );
  }
  if (empty) {
    return (
      <div
        className={cn(
          "py-10 text-center text-sm text-muted-foreground",
          className
        )}
      >
        {emptyMessage}
      </div>
    );
  }
  return <>{children}</>;
}
