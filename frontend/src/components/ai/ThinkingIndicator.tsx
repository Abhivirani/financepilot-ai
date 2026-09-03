"use client";

import { Sparkles } from "lucide-react";

/**
 * Animated "thinking" indicator shown while the AI is generating a response.
 * Three pulsing dots inside an assistant-style bubble.
 */
export function ThinkingIndicator() {
  return (
    <div className="flex max-w-[80%] gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ai-subtle text-ai">
        <Sparkles size={16} />
      </div>
      <div className="rounded-lg p-4 bg-bg-surface-sunken border border-border-default">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-ai animate-pulse" />
          <span className="h-2 w-2 rounded-full bg-ai animate-pulse [animation-delay:150ms]" />
          <span className="h-2 w-2 rounded-full bg-ai animate-pulse [animation-delay:300ms]" />
          <span className="ml-2 text-xs text-text-secondary">Thinking…</span>
        </div>
      </div>
    </div>
  );
}
