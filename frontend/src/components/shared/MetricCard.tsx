import * as React from "react";
import { LucideIcon, ArrowUpRight, ArrowDownRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  iconClassName?: string;
  trend?: {
    value: string;
    isPositive: boolean;
    label: string;
  };
  subtitle?: string;
  className?: string;
}

export function MetricCard({
  title,
  value,
  icon: Icon,
  iconClassName,
  trend,
  subtitle,
  className,
}: MetricCardProps) {
  return (
    <div className={cn("rounded-xl border border-border-default bg-bg-surface p-6 shadow-sm", className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-text-secondary">{title}</h3>
        <div className={cn("p-2 bg-bg-surface-sunken rounded-md", iconClassName)}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      <div className="text-2xl font-semibold font-mono tracking-tight">{value}</div>
      
      {trend && (
        <div className={cn(
          "flex items-center mt-1 text-sm",
          trend.isPositive ? "text-teal" : "text-crimson"
        )}>
          {trend.isPositive ? (
            <ArrowUpRight className="h-3 w-3 mr-1" />
          ) : (
            <ArrowDownRight className="h-3 w-3 mr-1" />
          )}
          <span>{trend.value} {trend.label}</span>
        </div>
      )}
      
      {subtitle && !trend && (
        <div className="flex items-center mt-1 text-sm text-text-secondary">
          <span>{subtitle}</span>
        </div>
      )}
    </div>
  );
}
