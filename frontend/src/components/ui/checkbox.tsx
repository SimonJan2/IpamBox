"use client";

import * as React from "react";
import { Check } from "lucide-react";
import { cn } from "@/lib/utils";

/** The control is custom-rendered (button + role=checkbox), so it must
 *  always carry an explicit accessible name — enforced at the type level. */
type AccessibleName =
  | { "aria-label": string; "aria-labelledby"?: string }
  | { "aria-label"?: string; "aria-labelledby": string };

interface CheckboxBaseProps
  extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, "onChange"> {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
}

export type CheckboxProps = CheckboxBaseProps & AccessibleName;

export const Checkbox = React.forwardRef<HTMLButtonElement, CheckboxProps>(
  ({ checked = false, onCheckedChange, className, disabled, ...props }, ref) => (
    <button
      type="button"
      role="checkbox"
      aria-checked={checked}
      ref={ref}
      disabled={disabled}
      {...props}
      onClick={(e) => {
        e.stopPropagation();
        props.onClick?.(e);
        onCheckedChange?.(!checked);
      }}
      className={cn(
        "flex h-4 w-4 shrink-0 items-center justify-center rounded-sm border border-primary/50 transition-colors",
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
        "disabled:cursor-not-allowed disabled:opacity-50",
        checked && "border-primary bg-primary text-primary-foreground",
        className
      )}
    >
      {checked && <Check className="h-3 w-3" />}
    </button>
  )
);
Checkbox.displayName = "Checkbox";
