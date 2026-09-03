"use client";

import * as React from "react";
import { useExceptions } from "@/hooks/useApi";
import { DataTable } from "@/components/table/DataTable";
import { StatusBadge } from "@/components/table/StatusBadge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Filter, Download } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";

export default function ExceptionsPage() {
  const [searchTerm, setSearchTerm] = React.useState("");
  const [page, setPage] = React.useState(1);
  const [debouncedSearch, setDebouncedSearch] = React.useState("");
  
  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(searchTerm);
      setPage(1); // Reset page on search
    }, 500);
    return () => clearTimeout(handler);
  }, [searchTerm]);

  const { data, isLoading } = useExceptions({
    page,
    page_size: 15,
    search: debouncedSearch || undefined
  });
  
  const exceptions = data?.items || [];
  const totalPages = data?.total_pages || 1;
  
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
      className: "text-right text-sm",
      cell: (row: any) => format(new Date(row.created_at), "MMM d, HH:mm")
    },
  ];
  
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Exceptions Inbox</h1>
          <p className="text-text-secondary">Review and resolve reconciliation discrepancies.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="bg-bg-surface">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button className="bg-brand hover:bg-brand-hover text-white" size="sm">
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
            <Button variant="outline" size="sm" className="w-full sm:w-auto">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
          </div>
        </div>
        
        <div className="p-0">
          <DataTable 
            data={exceptions} 
            columns={columns as any}
            isLoading={isLoading}
            onRowClick={(row) => console.log("Clicked row", row)}
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
    </div>
  );
}
