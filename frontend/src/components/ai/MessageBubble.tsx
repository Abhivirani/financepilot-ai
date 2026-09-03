"use client";

import { cn } from "@/lib/utils";
import { User, Sparkles } from "lucide-react";
import type { ChatMessage } from "@/types/ai";
import { ConfidenceBadge } from "./ConfidenceBadge";

interface MessageBubbleProps {
  message: ChatMessage;
}

/**
 * A single message bubble in the chat.
 * User messages align right with brand colour, assistant messages align left.
 */
export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex max-w-[80%] gap-3",
        isUser ? "ml-auto flex-row-reverse" : ""
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-brand text-white" : "bg-ai-subtle text-ai"
        )}
      >
        {isUser ? <User size={16} /> : <Sparkles size={16} />}
      </div>

      {/* Bubble */}
      <div
        className={cn(
          "rounded-lg p-4",
          isUser
            ? "bg-brand text-white"
            : "bg-bg-surface-sunken border border-border-default"
        )}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap">
          {message.content}
        </p>

        {/* Optional confidence badge */}
        {message.confidence && !isUser && (
          <div className="mt-2">
            <ConfidenceBadge level={message.confidence} />
          </div>
        )}

        {/* Suggested actions */}
        {message.suggestedActions && message.suggestedActions.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.suggestedActions.map((action, i) => (
              <span
                key={i}
                className="inline-flex items-center rounded-md border border-ai/20 bg-bg-surface px-2.5 py-0.5 text-xs font-medium text-ai"
              >
                {action}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
