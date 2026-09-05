"use client";

import * as React from "react";
import { useExceptions } from "@/hooks/useApi";
import { DataTable } from "@/components/table/DataTable";
import { StatusBadge } from "@/components/table/StatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Download, Sparkles, RefreshCw } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";
import { toast } from "sonner";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { exceptionsService } from "@/lib/api/services/exceptions";

import { ExplainDialog } from "@/components/ai/ExplainDialog";

export default function ExceptionsPage() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = React.useState("");
  const [page, setPage] = React.useState(1);
  const [debouncedSearch, setDebouncedSearch] = React.useState("");
  const [severityFilter, setSeverityFilter] = React.useState("");
  
  const [explainExceptionId, setExplainExceptionId] = React.useState<string | null>(null);
  const [isExplainOpen, setIsExplainOpen] = React.useState(false);
  
  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setPage(1); // Reset page on search
    }, 500);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  const { data, isLoading, refetch } = useExceptions({
    page,
    page_size: 15,
    search: debouncedSearch || undefined,
    severity: severityFilter || undefined
  });
  
  const exceptions = data?.items || [];
  const totalPages = data?.total_pages || 1;

  const handleExplain = (e: React.MouseEvent, exceptionId: string) => {
    e.stopPropagation();
    setExplainExceptionId(exceptionId);
    setIsExplainOpen(true);
  };
  
  const exportMutation = useMutation({
    mutationFn: async () => {
      const response = await exceptionsService.exportCSV();
      return response;
    },
    onSuccess: (data: any) => {
      const blob = new Blob([data], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `exceptions_export_${format(new Date(), "yyyy-MM-dd")}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success("Exceptions exported successfully");
    },
    onError: () => {
      toast.error("Failed to export exceptions");
    }
  });

  const autoResolveMutation = useMutation({
    mutationFn: async () => {
      const response = await exceptionsService.autoResolve();
      return response;
    },
    onSuccess: (data: any) => {
      toast.success(`Successfully auto-resolved ${data.resolved_count} exceptions`);
      queryClient.invalidateQueries({ queryKey: ["exceptions"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      refetch();
    },
    onError: () => {
      toast.error("Failed to auto-resolve exceptions");
    }
  });

  const columns = [
    { header: "Exception ID", accessorKey: "exception_id", className: "font-mono font-medium text-xs text-brand truncate max-w-[120px]" },
    { header: "Transaction ID", accessorKey: "transaction_id", className: "font-mono text-xs text-text-secondary truncate max-w-[120px]" },
    { header: "Rule Violated", accessorKey: "rule_type" },
    { 
      header: "Severity", 
      accessorKey: "severity",
      cell: (row: any) => {
        const severityMap: Record<string, "error" | "warning" | "info" | "neutral"> = {
          CRITICAL: "error",
          HIGH: "error",
          MEDIUM: "warning",
          LOW: "info"
        };
        return <StatusBadge status={severityMap[row.severity] || "neutral"} label={row.severity} />;
      }
    },
    { 
      header: "Status", 
      accessorKey: "status",
      cell: (row: any) => {
        const statusMap: Record<string, "success" | "warning" | "error" | "info" | "neutral"> = {
          OPEN: "error",
          IN_PROGRESS: "warning",
          RESOLVED: "success"
        };
        return <StatusBadge status={statusMap[row.status] || "neutral"} label={row.status} />;
      }
    },
    { 
      header: "Created", 
      accessorKey: "created_at", 
      className: "text-right text-sm hidden md:table-cell",
      cell: (row: any) => format(new Date(row.created_at), "MMM d, HH:mm")
    },
    {
      header: "Actions",
      accessorKey: "actions",
      className: "text-right",
      cell: (row: any) => (
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={(e) => handleExplain(e, row.exception_id)}
          className="text-brand hover:bg-brand/10 hover:text-brand px-2 py-1 h-8"
        >
          <Sparkles className="h-3.5 w-3.5 mr-1.5" />
          Explain
        </Button>
      )
    }
  ];
  
  return (
    <div className="space-y-6 relative">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Exceptions Inbox</h1>
          <p className="text-text-secondary">Review and resolve reconciliation discrepancies.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="sm" 
            className="bg-bg-surface" 
            onClick={() => exportMutation.mutate()}
            disabled={exportMutation.isPending || isLoading}
          >
            {exportMutation.isPending ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
            Export
          </Button>
          <Button 
            className="bg-brand hover:bg-brand-hover text-white" 
            size="sm"
            onClick={() => autoResolveMutation.mutate()}
            disabled={autoResolveMutation.isPending || isLoading}
          >
            {autoResolveMutation.isPending ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Sparkles className="h-4 w-4 mr-2" />}
            Auto-Resolve (2)
          </Button>
        </div>
      </div>
      
      <div className="rounded-xl border border-border-default bg-bg-surface overflow-hidden shadow-sm flex flex-col">
        <div className="p-4 border-b border-border-default flex flex-col sm:flex-row gap-3 items-center justify-between">
          <div className="relative w-full sm:max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-secondary" />
            <Input 
              placeholder="Search exceptions..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 bg-bg-surface-sunken border-transparent focus-visible:ring-brand"
            />
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <select 
              className="flex h-9 w-full sm:w-[150px] items-center justify-between rounded-md border border-border-default bg-bg-surface px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-1 focus:ring-brand"
              value={severityFilter}
              onChange={(e) => {
                setSeverityFilter(e.target.value);
                setPage(1);
              }}
            >
              <option value="">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>
        
        <div className="p-0">
          <DataTable 
            data={exceptions} 
            columns={columns as any}
            isLoading={isLoading}
            onRowClick={(row: any) => {
              setExplainExceptionId(row.exception_id);
              setIsExplainOpen(true);
            }}
          />
        </div>
        
        <div className="p-4 border-t border-border-default flex items-center justify-between">
          <div className="text-sm text-text-secondary">
            Page {page} of {totalPages}
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              disabled={page === 1 || isLoading}
              onClick={() => setPage(p => Math.max(1, p - 1))}
            >
              Previous
            </Button>
            <Button 
              variant="outline" 
              size="sm" 
              disabled={page >= totalPages || isLoading}
              onClick={() => setPage(p => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </div>

      <ExplainDialog 
        exceptionId={explainExceptionId}
        isOpen={isExplainOpen}
        onOpenChange={setIsExplainOpen}
      />
    </div>
  );
}
