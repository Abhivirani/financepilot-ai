"use client";

import { cn } from "@/lib/utils";

interface SuggestionChipProps {
  label: string;
  onClick?: () => void;
  className?: string;
}

/**
 * Clickable suggestion pill that auto-fills the chat input.
 */
export function SuggestionChip({ label, onClick, className }: SuggestionChipProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "inline-flex items-center rounded-full border border-ai/20",
        "bg-ai-subtle/50 px-3 py-1.5 text-xs font-medium text-ai",
        "transition-colors hover:bg-ai-subtle hover:border-ai/40",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ai/50",
        className
      )}
    >
      {label}
    </button>
  );
}
