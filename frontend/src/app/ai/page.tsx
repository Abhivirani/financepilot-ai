"use client";

import * as React from "react";
import { Sparkles, Send, User, Bot, AlertTriangle, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useAIExplain } from "@/hooks/useApi";

export default function AIAssistantPage() {
  const [messages, setMessages] = React.useState<{id: number, role: string, content: string, suggestedActions?: string[]}[]>([
    {
      id: 1,
      role: "assistant",
      content: "Hello! I'm FinancePilot AI. I can help explain reconciliation exceptions. Enter an exception ID (e.g. EX-...) to get started.",
    }
  ]);
  const [inputValue, setInputValue] = React.useState("");
  
  const { mutate: explainAI, isPending } = useAIExplain();

  const handleSend = () => {
    if (!inputValue.trim() || isPending) return;
    
    const query = inputValue.trim();
    
    setMessages(prev => [
      ...prev,
      { id: Date.now(), role: "user", content: query }
    ]);
    setInputValue("");
    
    explainAI(query, {
      onSuccess: (data) => {
        setMessages(prev => [
          ...prev,
          { 
            id: Date.now(), 
            role: "assistant", 
            content: data.explanation
          }
        ]);
      },
      onError: () => {
        setMessages(prev => [
          ...prev,
          { 
            id: Date.now(), 
            role: "assistant", 
            content: "I couldn't process that request. Please make sure you provided a valid Exception ID." 
          }
        ]);
      }
    });
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-ai" />
          AI Assistant
        </h1>
        <p className="text-text-secondary">Get intelligent insights on your reconciliation data.</p>
      </div>
      
      <div className="flex-1 rounded-xl border border-border-default bg-bg-surface overflow-hidden flex flex-col shadow-sm">
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={cn(
                "flex max-w-[80%] gap-4",
                message.role === "user" ? "ml-auto flex-row-reverse" : ""
              )}
            >
              <div className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
                message.role === "user" ? "bg-brand text-white" : "bg-ai-subtle text-ai"
              )}>
                {message.role === "user" ? <User size={16} /> : <Sparkles size={16} />}
              </div>
              <div className={cn(
                "rounded-lg p-4",
                message.role === "user" ? "bg-brand text-white" : "bg-bg-surface-sunken border border-border-default"
              )}>
                <p className="text-sm leading-relaxed">{message.content}</p>
                
                {message.suggestedActions && (
                  <div className="mt-4 flex flex-wrap gap-2">
                    {message.suggestedActions.map((action, i) => (
                      <Button key={i} variant="outline" size="sm" className="bg-bg-surface h-7 text-xs text-ai hover:text-ai border-ai/20">
                        {action}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div className="p-4 border-t border-border-default bg-bg-surface">
          <div className="flex gap-2">
            <Button variant="outline" size="icon" className="shrink-0 text-text-secondary" title="Attach file">
              <FileText className="h-4 w-4" />
            </Button>
            <div className="relative flex-1">
              <Input 
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask about an exception, batch, or trend..." 
                className="pr-12 border-border-default focus-visible:ring-ai"
                disabled={isPending}
              />
              <Button 
                onClick={handleSend}
                disabled={isPending}
                size="icon" 
                variant="ghost" 
                className="absolute right-1 top-1 h-8 w-8 text-ai hover:text-ai hover:bg-ai-subtle"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
