"use client";

import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

import { aiService } from "@/lib/api/services/ai";
import { AIExplainResponseData } from "@/types/ai";
import ReactMarkdown from "react-markdown";
import { Copy, RefreshCw, Sparkles, Clock, AlertCircle } from "lucide-react";
import { toast } from "sonner";

interface ExplainDialogProps {
  exceptionId: string | null;
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ExplainDialog({ exceptionId, isOpen, onOpenChange }: ExplainDialogProps) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<AIExplainResponseData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchExplanation = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await aiService.explain(id);
      setData(response.data);
    } catch (err: any) {
      console.error(err);
      if (err.response?.status === 401 || err.response?.status === 403) {
        setError("Authentication failed. Please check your API key.");
      } else if (err.response?.status === 429) {
        setError("Rate limit or quota exceeded. Please try again later.");
      } else if (err.code === "ECONNABORTED" || err.message.includes("timeout")) {
        setError("Network timeout. The request took too long.");
      } else {
        setError(err.response?.data?.message || err.message || "Failed to generate explanation.");
      }
      toast.error("Failed to generate AI explanation");
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    if (isOpen && exceptionId && !data && !loading && !error) {
      fetchExplanation(exceptionId);
    }
  }, [isOpen, exceptionId, data, loading, error]);

  const handleRegenerate = () => {
    if (exceptionId) {
      fetchExplanation(exceptionId);
    }
  };

  const handleCopy = () => {
    if (data?.markdown) {
      navigator.clipboard.writeText(data.markdown);
      toast.success("Explanation copied to clipboard");
    }
  };

  // Reset state when closed
  React.useEffect(() => {
    if (!isOpen) {
      setTimeout(() => {
        setData(null);
        setError(null);
      }, 200);
    }
  }, [isOpen]);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
    if (confidence >= 50) return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20";
    return "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20";
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[85vh] flex flex-col p-0 overflow-hidden bg-bg-surface border-border-default">
        <DialogHeader className="px-6 py-4 border-b border-border-default flex-none">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-brand" />
            <DialogTitle>AI Exception Analysis</DialogTitle>
          </div>
          <DialogDescription>
            {exceptionId ? `Explaining Exception ID: ${exceptionId}` : "Analyzing exception..."}
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto relative bg-bg-surface-sunken">
          {loading && (
            <div className="p-6 space-y-6">
              <div className="flex items-center gap-4 border-b border-border-default pb-4">
                <Skeleton className="h-10 w-10 rounded-full" />
                <div className="space-y-2">
                  <Skeleton className="h-4 w-[250px]" />
                  <Skeleton className="h-3 w-[150px]" />
                </div>
              </div>
              <div className="space-y-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-4/5" />
                <Skeleton className="h-4 w-full" />
              </div>
            </div>
          )}

          {error && !loading && (
            <div className="flex flex-col items-center justify-center p-12 text-center h-full">
              <AlertCircle className="h-12 w-12 text-rose-500 mb-4" />
              <h3 className="text-lg font-medium text-text-primary mb-2">Analysis Failed</h3>
              <p className="text-text-secondary mb-6 max-w-sm">{error}</p>
              <Button onClick={handleRegenerate} className="bg-brand text-white hover:bg-brand-hover">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
            </div>
          )}

          {data && !loading && !error && (
            <div className="h-full">
              <div className="p-6">
                <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:text-text-primary prose-p:text-text-secondary prose-a:text-brand prose-strong:text-text-primary">
                  <ReactMarkdown>{data.markdown}</ReactMarkdown>
                </div>
              </div>
            </div>
          )}
        </div>

        {data && !loading && !error && (
          <div className="p-4 border-t border-border-default bg-bg-surface flex-none flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <Badge variant="outline" className={getConfidenceColor(data.confidence)}>
                Confidence: {data.confidence}%
              </Badge>
              <div className="flex items-center text-xs text-text-muted">
                <Clock className="h-3 w-3 mr-1" />
                {data.latency_ms}ms
              </div>
            </div>
            
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Button variant="outline" size="sm" onClick={handleCopy} className="w-full sm:w-auto">
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </Button>
              <Button variant="outline" size="sm" onClick={handleRegenerate} className="w-full sm:w-auto text-brand border-brand/20 hover:bg-brand/5">
                <RefreshCw className="h-4 w-4 mr-2" />
                Regenerate
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
