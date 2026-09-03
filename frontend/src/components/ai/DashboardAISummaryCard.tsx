"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { aiService } from "@/lib/api/services/ai";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import ReactMarkdown from "react-markdown";
import { Copy, RefreshCw, Sparkles, Clock, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { format } from "date-fns";

export function DashboardAISummaryCard() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["dashboard-ai-summary"],
    queryFn: async () => {
      const response = await aiService.getDashboardSummary();
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  const handleCopy = () => {
    if (data?.markdown) {
      navigator.clipboard.writeText(data.markdown);
      toast.success("Summary copied to clipboard");
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
    if (confidence >= 50) return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20";
    return "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20";
  };

  return (
    <Card className="w-full bg-gradient-to-br from-ai-subtle to-bg-surface border-ai/20 shadow-sm relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
        <Sparkles className="w-32 h-32 text-ai" />
      </div>
      
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="flex items-center gap-2 z-10">
          <div className="p-1.5 rounded-md bg-ai/10 text-ai">
            <Sparkles className="h-5 w-5" />
          </div>
          <CardTitle className="text-xl text-text-primary">AI Financial Summary</CardTitle>
        </div>
        
        <div className="flex gap-2 z-10">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={handleCopy}
            disabled={!data || isLoading || !!error}
            className="bg-bg-surface h-8"
          >
            <Copy className="h-3.5 w-3.5 mr-1.5" />
            Copy
          </Button>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()}
            disabled={isLoading}
            className="bg-bg-surface text-brand border-brand/20 hover:bg-brand/5 h-8"
          >
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${isLoading ? 'animate-spin' : ''}`} />
            Regenerate
          </Button>
        </div>
      </CardHeader>

      <CardContent className="pt-4 z-10 relative">
        {isLoading && (
          <div className="space-y-4">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-4/5" />
          </div>
        )}

        {error && !isLoading && (
          <div className="flex flex-col items-center justify-center p-6 text-center border border-dashed border-rose-200 rounded-lg bg-rose-50/50 dark:bg-rose-950/10 dark:border-rose-900">
            <AlertCircle className="h-8 w-8 text-rose-500 mb-2" />
            <h3 className="text-sm font-medium text-text-primary mb-1">Unable to generate summary</h3>
            <p className="text-xs text-text-secondary mb-4 max-w-sm">
              {(error as any)?.response?.data?.message || (error as Error).message || "Failed to reach AI service."}
            </p>
            <Button onClick={() => refetch()} size="sm" variant="outline" className="h-8 border-rose-200 hover:bg-rose-50">
              <RefreshCw className="h-3.5 w-3.5 mr-1.5" />
              Try Again
            </Button>
          </div>
        )}

        {data && !isLoading && !error && (
          <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:text-text-primary prose-p:text-text-secondary prose-a:text-brand prose-strong:text-text-primary prose-headings:font-medium prose-headings:text-sm prose-headings:mt-4 prose-headings:mb-2 prose-p:mb-3">
            <ReactMarkdown>{data.markdown}</ReactMarkdown>
          </div>
        )}
      </CardContent>

      <CardFooter className="bg-bg-surface/50 border-t border-border-default/50 px-6 py-3 flex flex-wrap items-center justify-between gap-4 z-10 relative">
        <div className="flex items-center gap-3">
          {data ? (
            <Badge variant="outline" className={getConfidenceColor(data.confidence)}>
              Confidence: {data.confidence}%
            </Badge>
          ) : (
            <Skeleton className="h-5 w-24 rounded-full" />
          )}
          
          <div className="flex items-center text-xs text-text-muted">
            <Clock className="h-3 w-3 mr-1" />
            {data ? `${data.latency_ms}ms` : "--- ms"}
          </div>
        </div>
        
        <div className="text-xs text-text-muted">
          {data?.generated_at ? `Generated ${format(new Date(data.generated_at), "MMM d, HH:mm:ss")}` : ""}
        </div>
      </CardFooter>
    </Card>
  );
}
