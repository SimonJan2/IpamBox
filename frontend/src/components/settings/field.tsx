"use client";

import { cloneElement, isValidElement, useId } from "react";
import { RotateCcw } from "lucide-react";

import type { SettingSource } from "@/types";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const SOURCE_STYLE: Record<SettingSource, { label: string; className: string }> = {
  db: { label: "custom", className: "border-emerald-500/40 text-emerald-400" },
  env: { label: ".env", className: "border-sky-500/40 text-sky-400" },
  default: { label: "default", className: "text-muted-foreground" },
};

/** One settings row: label + control + source badge + reset-to-env button. */
export function SettingField({
  label,
  hint,
  source,
  onReset,
  error,
  children,
}: {
  label: string;
  hint?: string;
  source?: SettingSource;
  onReset?: () => void;
  error?: string;
  children: React.ReactNode;
}) {
  const controlId = useId();
  return (
    <div className="grid gap-1.5">
      <div className="flex items-center justify-between gap-2">
        <Label className="text-sm" htmlFor={controlId}>
          {label}
        </Label>
        {source && (
          <span className="flex items-center gap-1.5">
            <Tooltip>
              <TooltipTrigger asChild>
                <Badge
                  variant="outline"
                  className={cn("text-[10px] font-normal", SOURCE_STYLE[source].className)}
                >
                  {SOURCE_STYLE[source].label}
                </Badge>
              </TooltipTrigger>
              <TooltipContent>
                {source === "db" && "Set in the UI — overrides .env"}
                {source === "env" && "Set via .env — reset removes the UI override"}
                {source === "default" && "Built-in default — not configured anywhere"}
              </TooltipContent>
            </Tooltip>
            {source === "db" && onReset && (
              <Button
                variant="ghost"
                size="icon"
                className="h-6 w-6"
                aria-label={`Reset ${label} to .env / default`}
                title="Reset to .env / default"
                onClick={onReset}
              >
                <RotateCcw className="h-3 w-3" />
              </Button>
            )}
          </span>
        )}
      </div>
      {isValidElement(children)
        ? cloneElement(
            children as React.ReactElement<{
              id?: string;
              "aria-label"?: string;
              "aria-labelledby"?: string;
            }>,
            {
              id: controlId,
              // htmlFor doesn't reliably name button-based controls (Switch,
              // Select root) — pass the label through as aria-label too.
              ...((children.props as Record<string, unknown>)["aria-label"] ==
                null &&
              (children.props as Record<string, unknown>)["aria-labelledby"] ==
                null
                ? { "aria-label": label }
                : {}),
            }
          )
        : children}
      {error ? (
        <p className="text-xs text-rose-400">{error}</p>
      ) : hint ? (
        <p className="text-xs text-muted-foreground">{hint}</p>
      ) : null}
    </div>
  );
}
