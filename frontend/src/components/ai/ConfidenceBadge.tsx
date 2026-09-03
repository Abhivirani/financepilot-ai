"use client";

import { cn } from "@/lib/utils";
import { ShieldCheck, ShieldAlert, ShieldQuestion } from "lucide-react";
import type { ConfidenceLevel } from "@/types/ai";

interface ConfidenceBadgeProps {
  level: ConfidenceLevel;
  className?: string;
}

const config: Record<ConfidenceLevel, { label: string; icon: typeof ShieldCheck; className: string }> = {
  high: {
    label: "High confidence",
    icon: ShieldCheck,
    className: "text-teal border-teal/20 bg-teal-subtle",
  },
  medium: {
    label: "Medium confidence",
    icon: ShieldAlert,
    className: "text-amber border-amber/20 bg-amber-subtle",
  },
  low: {
    label: "Low confidence",
    icon: ShieldQuestion,
    className: "text-text-secondary border-border-default bg-bg-surface-sunken",
  },
};

/**
 * Visual indicator of how confident the AI is in its response.
 */
export function ConfidenceBadge({ level, className }: ConfidenceBadgeProps) {
  const { label, icon: Icon, className: levelClass } = config[level];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-[10px] font-medium",
        levelClass,
        className
      )}
    >
      <Icon size={12} />
      {label}
    </span>
  );
}
