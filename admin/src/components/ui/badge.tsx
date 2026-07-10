import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize",
  {
    variants: {
      variant: {
        default: "border-transparent bg-accent text-primary",
        success: "border-transparent bg-success/15 text-success",
        warning: "border-transparent bg-warning/15 text-warning",
        destructive: "border-transparent bg-destructive/15 text-destructive",
        outline: "border-border text-muted-foreground",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

const STATUS_VARIANT: Record<string, BadgeProps["variant"]> = {
  active: "success",
  approved: "success",
  settled: "success",
  successful: "success",
  pending_kyc: "warning",
  pending: "warning",
  submitted: "warning",
  under_review: "warning",
  requires_more_info: "warning",
  frozen: "warning",
  declined: "destructive",
  rejected: "destructive",
  failed: "destructive",
  suspended: "destructive",
  closed: "outline",
  restricted: "destructive",
  blocked: "destructive",
  open: "warning",
  in_progress: "warning",
  reviewing: "warning",
  resolved: "success",
  dismissed: "outline",
};

export function StatusBadge({ status }: { status: string }) {
  return <Badge variant={STATUS_VARIANT[status] ?? "default"}>{status.replace(/_/g, " ")}</Badge>;
}
