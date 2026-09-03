"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { ChatMessage } from "@/types/ai";
import { MessageBubble } from "./MessageBubble";
import { ThinkingIndicator } from "./ThinkingIndicator";
import { SuggestionChip } from "./SuggestionChip";

interface ChatWindowProps {
  messages: ChatMessage[];
  isThinking?: boolean;
  suggestedQuestions?: string[];
  onSuggestionClick?: (question: string) => void;
  className?: string;
}

/**
 * Scrollable chat message list with thinking indicator and suggestion chips.
 * 
 * This component is a pure renderer — state management and API calls happen
 * in the parent page (app/ai/page.tsx).
 */
export function ChatWindow({
  messages,
  isThinking = false,
  suggestedQuestions = [],
  onSuggestionClick,
  className,
}: ChatWindowProps) {
  const scrollRef = React.useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  return (
    <div
      ref={scrollRef}
      className={cn("flex-1 overflow-y-auto p-6 space-y-6", className)}
    >
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}

      {isThinking && <ThinkingIndicator />}

      {suggestedQuestions.length > 0 && !isThinking && (
        <div className="flex flex-wrap gap-2 pt-2">
          {suggestedQuestions.map((question, i) => (
            <SuggestionChip
              key={i}
              label={question}
              onClick={() => onSuggestionClick?.(question)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
