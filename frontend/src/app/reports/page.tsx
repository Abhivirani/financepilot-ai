"use client";

import React, { useRef } from "react";
import { Sparkles, Download, FileText, FileDown, RefreshCw, Clock, Copy, AlignLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { toast } from "sonner";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { aiService } from "@/lib/api/services/ai";
import { format } from "date-fns";

export default function ReportsPage() {
  const queryClient = useQueryClient();
  const reportRef = useRef<HTMLDivElement>(null);

  const { data, mutate: generateReport, isPending, error } = useMutation({
    mutationKey: ["executive-report"],
    mutationFn: async () => {
      const res = await aiService.generateExecutiveReport();
      return res;
    },
    onSuccess: (data) => {
      toast.success("Executive report generated successfully.");
      // In a broader app, we might store this in query cache.
      queryClient.setQueryData(["latest-executive-report"], data);
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.message || err.message || "Failed to generate report.");
    }
  });

  const handleDownloadPDF = async () => {
    if (typeof window === "undefined" || !reportRef.current) return;
    try {
      const html2pdf = (await import("html2pdf.js")).default;
      const opt = {
        margin: [10, 10, 10, 10] as [number, number, number, number],
        filename: `executive-report-${format(new Date(), "yyyy-MM-dd")}.pdf`,
        image: { type: 'jpeg' as const, quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' as const }
      };
      html2pdf().set(opt).from(reportRef.current).save();
    } catch (e) {
      toast.error("Failed to generate PDF. Make sure your browser supports this feature.");
    }
  };

  const handleDownloadMarkdown = () => {
    if (!data?.markdown) return;
    const blob = new Blob([data.markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `executive-report-${format(new Date(), "yyyy-MM-dd")}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopyMarkdown = () => {
    if (data?.markdown) {
      navigator.clipboard.writeText(data.markdown);
      toast.success("Markdown copied to clipboard");
    }
  };

  const handleCopyPlainText = () => {
    if (reportRef.current) {
      const text = reportRef.current.innerText;
      navigator.clipboard.writeText(text);
      toast.success("Plain text copied to clipboard");
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";
    if (confidence >= 70) return "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20";
    return "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20";
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Executive Reports</h1>
          <p className="text-text-secondary">Generate and export AI-powered reconciliation summaries.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            onClick={() => generateReport()} 
            disabled={isPending}
            className="bg-brand hover:bg-brand-hover text-white shadow-md shadow-brand/20 transition-all"
          >
            {isPending ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4 mr-2" />
            )}
            {data ? "Regenerate Report" : "Generate Executive Report"}
          </Button>
        </div>
      </div>
      
      {!data && !isPending && !error && (
        <Card className="border-dashed border-2 bg-bg-surface/50 shadow-none">
          <CardContent className="flex flex-col items-center justify-center py-20 text-center">
            <div className="h-16 w-16 bg-ai/10 text-ai rounded-full flex items-center justify-center mb-4">
              <FileText className="h-8 w-8" />
            </div>
            <h3 className="text-lg font-medium text-text-primary mb-2">No Report Generated</h3>
            <p className="text-text-secondary max-w-sm mb-6">
              Generate an intelligent executive summary of the latest reconciliation run using FinancePilot AI.
            </p>
            <Button onClick={() => generateReport()} className="bg-brand hover:bg-brand-hover text-white">
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
          </CardContent>
        </Card>
      )}

      {isPending && (
        <Card className="border-border-default shadow-sm bg-bg-surface">
          <CardHeader>
            <Skeleton className="h-8 w-1/3 mb-2" />
            <Skeleton className="h-4 w-1/4" />
          </CardHeader>
          <CardContent className="space-y-6">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-[90%]" />
            <Skeleton className="h-4 w-[95%]" />
            
            <Skeleton className="h-6 w-1/4 mt-8 mb-4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-[85%]" />
            
            <Skeleton className="h-32 w-full mt-6 rounded-lg" />
          </CardContent>
        </Card>
      )}

      {data && !isPending && (
        <div className="space-y-6">
          <Card className="border-border-default shadow-sm bg-white dark:bg-slate-900 overflow-hidden">
            {/* The printable area */}
            <div ref={reportRef} className="p-8 sm:p-12">
              {/* Report Header for PDF */}
              <div className="border-b border-border-strong pb-6 mb-8 flex justify-between items-end">
                <div>
                  <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white mb-2">
                    {data.title || "Executive Reconciliation Report"}
                  </h2>
                  <p className="text-slate-500 dark:text-slate-400">
                    Generated {format(new Date(data.generated_at), "MMMM d, yyyy")}
                  </p>
                </div>
                <div className="text-right hidden sm:block">
                  <div className="flex flex-col gap-1 items-end">
                    <Badge variant="outline" className={cn("px-2 py-0.5 border text-xs", getConfidenceColor(data.confidence))}>
                      Confidence: {data.confidence}%
                    </Badge>
                    <span className="text-xs text-slate-400 flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      Latency: {data.latency_ms} ms
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Markdown Content */}
              <div className="prose prose-slate dark:prose-invert max-w-none 
                              prose-headings:text-slate-800 dark:prose-headings:text-slate-100 prose-headings:font-semibold
                              prose-h1:text-2xl prose-h1:border-b prose-h1:pb-2 prose-h1:mb-4 prose-h1:mt-8
                              prose-h2:text-xl prose-h2:mb-3
                              prose-p:text-slate-600 dark:prose-p:text-slate-300 prose-p:leading-relaxed
                              prose-li:text-slate-600 dark:prose-li:text-slate-300
                              prose-strong:text-slate-900 dark:prose-strong:text-white
                              print:prose-headings:text-black print:prose-p:text-gray-800">
                <ReactMarkdown>{data.markdown}</ReactMarkdown>
              </div>
            </div>
            
            {/* Actions Footer (Not printed) */}
            <div className="bg-slate-50 dark:bg-slate-800/50 border-t border-border-default p-4 sm:px-8 flex flex-wrap gap-2 items-center justify-between">
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" onClick={handleCopyMarkdown}>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy Markdown
                </Button>
                <Button variant="outline" size="sm" onClick={handleCopyPlainText}>
                  <AlignLeft className="h-4 w-4 mr-2" />
                  Copy Plain Text
                </Button>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" onClick={handleDownloadMarkdown} className="text-ai border-ai/20 hover:bg-ai/5">
                  <FileDown className="h-4 w-4 mr-2" />
                  Download Markdown
                </Button>
                <Button variant="default" size="sm" onClick={handleDownloadPDF} className="bg-slate-900 hover:bg-slate-800 dark:bg-white dark:hover:bg-slate-200 dark:text-slate-900">
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
