"use client";

import React, { useState, useRef, useEffect } from "react";
import { Sparkles, Send, User, Copy, RefreshCw, Clock, Bot, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { format } from "date-fns";
import { toast } from "sonner";
import { aiService } from "@/lib/api/services/ai";
import { useMutation } from "@tanstack/react-query";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  confidence?: number;
  latency_ms?: number;
  isError?: boolean;
};

const SUGGESTIONS = [
  "Why is today's match rate low?",
  "Summarize today's reconciliation.",
  "Highest financial risk?",
  "Explain Missing Settlement.",
  "How much money is unreconciled?",
  "Top exception rule?",
];

export default function AICopilotPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const { mutate: sendMessage, isPending } = useMutation({
    mutationFn: async (message: string) => {
      const res = await aiService.chat(message);
      return res;
    },
    onSuccess: (data, variables) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "assistant",
          content: data.answer,
          timestamp: new Date(data.generated_at || Date.now()),
          confidence: data.confidence,
          latency_ms: data.latency_ms,
        },
      ]);
    },
    onError: (error: any) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "assistant",
          content: error?.response?.data?.message || error.message || "Failed to communicate with AI.",
          timestamp: new Date(),
          isError: true,
        },
      ]);
    },
  });

  const handleSend = (text: string = input) => {
    if (!text.trim() || isPending) return;

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        role: "user",
        content: text.trim(),
        timestamp: new Date(),
      },
    ]);
    
    setInput("");
    sendMessage(text.trim());
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Message copied to clipboard");
  };

  const handleRegenerate = () => {
    const lastUserMessage = [...messages].reverse().find((m) => m.role === "user");
    if (lastUserMessage) {
      // Remove the last assistant response if it exists
      setMessages(messages.filter((m) => m.id !== lastUserMessage.id && m.timestamp <= lastUserMessage.timestamp));
      sendMessage(lastUserMessage.content);
    }
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return "bg-gray-100 text-gray-500 border-gray-200 dark:bg-gray-800 dark:text-gray-400";
    if (confidence >= 80) return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
    if (confidence >= 50) return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20";
    return "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20";
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-ai" />
          FinancePilot AI Copilot
        </h1>
        <p className="text-text-secondary">Your intelligent assistant for financial reconciliation insights.</p>
      </div>

      <div className="flex-1 rounded-xl border border-border-default bg-bg-surface overflow-hidden flex flex-col shadow-sm">
        
        {/* Conversation Area */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
          
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center max-w-2xl mx-auto text-center space-y-6 mt-10">
              <div className="h-16 w-16 bg-ai/10 text-ai rounded-full flex items-center justify-center mb-2">
                <Bot className="h-8 w-8" />
              </div>
              <h2 className="text-xl font-medium text-text-primary">Ask FinancePilot AI</h2>
              <p className="text-text-secondary">I can analyze your reconciliation results, explain exceptions, and assess financial risks in real-time.</p>
              
              <div className="flex flex-wrap justify-center gap-2 mt-8">
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => handleSend(suggestion)}
                    className="px-4 py-2 bg-bg-surface-sunken hover:bg-border-default border border-border-default rounded-full text-sm text-text-primary transition-colors text-left"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message, i) => (
              <div 
                key={message.id} 
                className={cn(
                  "flex max-w-[85%] lg:max-w-[75%] gap-4",
                  message.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                )}
              >
                <div className={cn(
                  "flex h-8 w-8 shrink-0 items-center justify-center rounded-full mt-1",
                  message.role === "user" ? "bg-bg-surface-sunken border border-border-strong text-text-secondary" : "bg-ai text-white"
                )}>
                  {message.role === "user" ? <User size={16} /> : <Sparkles size={16} />}
                </div>
                
                <div className="flex flex-col gap-1 min-w-0 group">
                  <div className={cn(
                    "rounded-2xl p-4 shadow-sm",
                    message.role === "user" 
                      ? "bg-bg-surface-sunken border border-border-default text-text-primary rounded-tr-sm" 
                      : message.isError 
                        ? "bg-rose-50 border border-rose-200 dark:bg-rose-950/20 dark:border-rose-900 text-rose-700 dark:text-rose-400 rounded-tl-sm"
                        : "bg-white dark:bg-slate-900 border border-ai/20 rounded-tl-sm"
                  )}>
                    {message.isError && (
                      <div className="flex items-center gap-2 mb-2 font-medium">
                        <AlertCircle className="h-4 w-4" /> Error
                      </div>
                    )}
                    <div className="prose prose-sm dark:prose-invert max-w-none break-words
                                    prose-p:leading-relaxed prose-headings:text-text-primary 
                                    prose-strong:text-text-primary prose-a:text-ai hover:prose-a:text-ai-subtle">
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                  </div>

                  {/* Message Metadata & Actions (Only for Assistant) */}
                  <div className={cn(
                    "flex items-center gap-3 text-xs text-text-muted mt-1 px-1",
                    message.role === "user" && "justify-end"
                  )}>
                    <span>{format(message.timestamp, "HH:mm")}</span>
                    
                    {message.role === "assistant" && !message.isError && (
                      <>
                        <span className="w-1 h-1 rounded-full bg-border-strong" />
                        <span className="flex items-center">
                          <Clock className="h-3 w-3 mr-1" />
                          {message.latency_ms}ms
                        </span>
                        <span className="w-1 h-1 rounded-full bg-border-strong" />
                        <Badge variant="outline" className={cn("text-[10px] h-5 px-1.5 py-0 border", getConfidenceColor(message.confidence))}>
                          Confidence: {message.confidence}%
                        </Badge>
                        <div className="flex-1" />
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button variant="ghost" size="icon" className="h-6 w-6 text-text-muted hover:text-text-primary" onClick={() => handleCopy(message.content)}>
                            <Copy className="h-3 w-3" />
                          </Button>
                          {i === messages.length - 1 && (
                            <Button variant="ghost" size="icon" className="h-6 w-6 text-text-muted hover:text-text-primary" onClick={handleRegenerate}>
                              <RefreshCw className="h-3 w-3" />
                            </Button>
                          )}
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}

          {/* Loading Indicator */}
          {isPending && (
            <div className="flex max-w-[85%] lg:max-w-[75%] gap-4 mr-auto">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full mt-1 bg-ai text-white">
                <Sparkles size={16} />
              </div>
              <div className="rounded-2xl p-4 bg-white dark:bg-slate-900 border border-ai/20 rounded-tl-sm w-[250px]">
                <div className="flex flex-col gap-2">
                  <Skeleton className="h-4 w-full bg-ai/10" />
                  <Skeleton className="h-4 w-4/5 bg-ai/10" />
                  <Skeleton className="h-4 w-3/5 bg-ai/10" />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-border-default bg-bg-surface">
          <div className="max-w-4xl mx-auto relative flex items-end gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask FinancePilot AI a question... (Shift+Enter for new line)"
              className="w-full resize-none min-h-[52px] max-h-[200px] overflow-y-auto rounded-xl border border-border-strong bg-bg-surface-sunken px-4 py-3.5 pr-14 text-sm focus:outline-none focus:ring-2 focus:ring-ai/50 placeholder:text-text-disabled"
              rows={1}
              style={{
                height: "auto",
              }}
              onInput={(e) => {
                const target = e.target as HTMLTextAreaElement;
                target.style.height = 'auto';
                target.style.height = `${Math.min(target.scrollHeight, 200)}px`;
              }}
              disabled={isPending}
            />
            <Button
              onClick={() => handleSend()}
              disabled={!input.trim() || isPending}
              size="icon"
              className="absolute right-2 bottom-2 h-9 w-9 bg-ai hover:bg-ai-subtle hover:text-ai text-white transition-colors rounded-lg disabled:opacity-50"
            >
              <Send className="h-4 w-4 ml-0.5" />
            </Button>
          </div>
          <div className="max-w-4xl mx-auto mt-2 text-center">
            <p className="text-[11px] text-text-disabled">
              FinancePilot AI can make mistakes. Consider verifying important financial insights.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
