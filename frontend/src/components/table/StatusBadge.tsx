import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type StatusType = "success" | "warning" | "error" | "info" | "neutral";

interface StatusBadgeProps {
  status: StatusType;
  label: string;
  className?: string;
}

const statusStyles: Record<StatusType, string> = {
  success: "bg-teal-subtle text-teal border-teal/20",
  warning: "bg-amber-subtle text-amber border-amber/20",
  error: "bg-crimson-subtle text-crimson border-crimson/20",
  info: "bg-brand-subtle text-brand border-brand/20",
  neutral: "bg-bg-surface-sunken text-text-secondary border-border-default",
};

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  return (
    <Badge
      variant="outline"
      className={cn("font-medium", statusStyles[status], className)}
    >
      {label}
    </Badge>
  );
}
