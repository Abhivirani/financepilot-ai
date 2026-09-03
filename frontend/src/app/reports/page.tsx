"use client";

import * as React from "react";
import { FileText, Download, Filter, Calendar as CalendarIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/shared/EmptyState";
import { DataTable } from "@/components/table/DataTable";
import { useReports } from "@/hooks/useApi";
import { Skeleton } from "@/components/ui/skeleton";

export default function ReportsPage() {
  const { data: reportsData, isLoading } = useReports();
  const reports = reportsData || [];

  const columns = [
    { header: "Report Name", accessorKey: "name", className: "font-medium text-text-primary" },
    { header: "Date Generated", accessorKey: "date", className: "text-text-secondary" },
    { header: "Format", accessorKey: "type", className: "font-mono text-xs" },
    { header: "Size", accessorKey: "size", className: "text-right text-text-secondary" },
    { 
      header: "", 
      accessorKey: "actions",
      className: "text-right",
      cell: (row: any) => (
        <a 
          href={row.url ? `http://localhost:8000${row.url}` : "#"}
          target="_blank"
          rel="noopener noreferrer"
        >
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-text-secondary hover:text-brand" title="Download">
            <Download className="h-4 w-4" />
          </Button>
        </a>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Reports</h1>
          <p className="text-text-secondary">Generate and download audit reports.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="bg-bg-surface">
            <CalendarIcon className="h-4 w-4 mr-2" />
            Date Range
          </Button>
          <Button className="bg-brand hover:bg-brand-hover text-white" size="sm">
            Generate New
          </Button>
        </div>
      </div>
      
      <div className="rounded-xl border border-border-default bg-bg-surface overflow-hidden shadow-sm">
        <div className="p-4 border-b border-border-default flex justify-between items-center bg-bg-surface">
          <h3 className="font-semibold text-text-primary">Available Reports</h3>
          <Button variant="ghost" size="sm" className="text-text-secondary">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
        </div>
        
        <div className="p-0">
          <DataTable 
            data={reports} 
            columns={columns as any}
            isLoading={isLoading}
            emptyMessage="No reports generated yet."
          />
        </div>
      </div>
    </div>
  );
}
