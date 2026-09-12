import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary/15 text-emerald-400",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        outline: "text-foreground",
        amber: "border-transparent bg-amber-500/15 text-amber-400",
        violet: "border-transparent bg-violet-500/15 text-violet-400",
        cyan: "border-transparent bg-cyan-500/15 text-cyan-400",
        red: "border-transparent bg-red-500/15 text-red-400",
        zinc: "border-transparent bg-zinc-500/15 text-zinc-400",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
