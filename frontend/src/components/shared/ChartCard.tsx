import * as React from "react";
import { cn } from "@/lib/utils";

interface ChartCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export function ChartCard({
  title,
  description,
  children,
  className,
}: ChartCardProps) {
  return (
    <div className={cn("rounded-xl border border-border-default bg-bg-surface flex flex-col overflow-hidden shadow-sm", className)}>
      <div className="p-6 border-b border-border-default flex-shrink-0">
        <h3 className="font-semibold">{title}</h3>
        {description && <p className="text-sm text-text-secondary">{description}</p>}
      </div>
      <div className="p-6 flex-1 flex flex-col">
        {children}
      </div>
    </div>
  );
}
