"use client";

import * as React from "react";
import { useDashboard } from "@/hooks/useApi";
import { MetricCardSkeleton, ChartCardSkeleton } from "@/components/shared/LoadingSkeletons";
import { ErrorState } from "@/components/shared/ErrorState";
import { MetricCard } from "@/components/shared/MetricCard";
import { Activity, AlertTriangle, FileText, CheckCircle2, Sparkles, RefreshCw, Upload } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import Link from "next/link";
import { StatusBadge } from "@/components/table/StatusBadge";
import { DataTable } from "@/components/table/DataTable";
import { ExceptionBarChart } from "@/components/charts/ExceptionBarChart";
import { format } from "date-fns";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { uploadService } from "@/lib/api/services/upload";
import { reconcileService } from "@/lib/api/services/reconcile";

import { DashboardAISummaryCard } from "@/components/ai/DashboardAISummaryCard";
import { formatCurrency } from "@/lib/formatCurrency";

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const { data, isLoading, isError, error, refetch } = useDashboard();
  const [isDemoLoading, setIsDemoLoading] = React.useState(false);

  const handleUseDemoDataset = async () => {
    setIsDemoLoading(true);
    try {
      const demoRes = await uploadService.uploadDemo();
      const batchId = demoRes.batch_id;
      await reconcileService.reconcile({ batch_id: batchId });
      toast.success("Demo dataset generated and reconciled successfully!");
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-ai-summary"] });
      queryClient.invalidateQueries({ queryKey: ["exceptions"] });
      queryClient.invalidateQueries({ queryKey: ["reports"] });
      refetch();
    } catch (err: any) {
      toast.error(err?.response?.data?.message || err?.message || "Failed to run demo reconciliation");
    } finally {
      setIsDemoLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-text-secondary">Overview of reconciliation status</p>
        </div>
        <Skeleton className="w-full h-48 rounded-xl" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCardSkeleton />
          <MetricCardSkeleton />
          <MetricCardSkeleton />
          <MetricCardSkeleton />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2"><ChartCardSkeleton /></div>
          <div><ChartCardSkeleton /></div>
        </div>
      </div>
    );
  }

  if (isError) {
    console.error("Dashboard error:", error);
    return (
      <div className="mt-12">
        <ErrorState 
          title="Failed to load dashboard" 
          message={error instanceof Error ? error.message : "There was a problem communicating with the backend API."} 
          onRetry={refetch} 
        />
      </div>
    );
  }

  const stats = data?.financial_summary || {
    total_amount_processed: 0,
    matched_amount: 0,
    unmatched_amount: 0,
    discrepancy_amount: 0,
    currency: "INR",
  };

  const metrics = data?.metrics || {
    match_rate: 0,
    total_exceptions: 0,
    total_transactions: 0,
    matched_transactions: 0,
    unmatched_transactions: 0,
  };

  const isEmptyState = !data || data.run_id === "empty-run" || metrics.total_transactions === 0;
  const recentExceptions = data?.recent_exceptions || [];
  const ruleDistribution = data?.rule_distribution || [];

  const chartData = ruleDistribution.map((item: any, i: number) => {
    const colors = ["#EF4444", "#F59E0B", "#3B82F6", "#10B981", "#8B5CF6", "#EC4899"];
    const ruleLabelMap: Record<string, string> = {
      "AMOUNT_MISMATCH": "Amt Mismatch",
      "FEE_MISMATCH": "Fee Mismatch",
      "MISSING_SETTLEMENT": "Missing Settlement",
      "DUPLICATE_TRANSACTION": "Duplicate",
      "DUPLICATE": "Duplicate",
      "MISSING_INVOICE": "Missing Invoice",
      "LATE_SETTLEMENT": "Settlement Delay",
      "ORPHAN": "Orphan Record"
    };
    const rawRule = String(item.rule_type);
    const ruleLabel = ruleLabelMap[rawRule] || rawRule.replace(/_/g, " ");
    return {
      rule: ruleLabel,
      count: item.count,
      color: colors[i % colors.length]
    };
  });

  const columns = [
    { 
      header: "Transaction ID", 
      accessorKey: "transaction_id", 
      className: "font-mono text-xs font-semibold whitespace-nowrap px-3 py-2" 
    },
    { 
      header: "Rule Type", 
      accessorKey: "rule_type", 
      className: "font-medium text-xs whitespace-nowrap px-3 py-2",
      cell: (row: any) => {
        const ruleMap: Record<string, string> = {
          "AMOUNT_MISMATCH": "Amount Mismatch",
          "FEE_MISMATCH": "Fee Mismatch",
          "MISSING_SETTLEMENT": "Missing Settlement",
          "DUPLICATE_TRANSACTION": "Duplicate Gateway",
          "DUPLICATE": "Duplicate Gateway",
          "MISSING_INVOICE": "Missing Invoice",
          "LATE_SETTLEMENT": "Settlement Delay",
          "ORPHAN": "Orphan Record"
        };
        const raw = String(row.rule_type);
        return ruleMap[raw] || raw.replace(/_/g, " ");
      }
    },
    { 
      header: "Bank Amount", 
      accessorKey: "amount", 
      className: "text-right font-mono text-xs font-medium whitespace-nowrap px-3 py-2",
      cell: (row: any) => formatCurrency(row.amount || 0)
    },
    { 
      header: "Gateway Amount", 
      accessorKey: "gateway_amount", 
      className: "text-right font-mono text-xs text-text-secondary whitespace-nowrap px-3 py-2",
      cell: (row: any) => row.gateway_amount > 0 ? formatCurrency(row.gateway_amount) : "—"
    },
    { 
      header: "Difference", 
      accessorKey: "difference", 
      className: "text-right font-mono text-xs font-medium whitespace-nowrap px-3 py-2",
      cell: (row: any) => {
        const rawRule = String(row.rule_type);
        if (rawRule === "FEE_MISMATCH") {
          return <span className="text-text-muted">N/A</span>;
        }
        if (row.difference === null || row.difference === undefined) {
          return <span className="text-text-muted">—</span>;
        }
        const diff = Number(row.difference || 0);
        if (diff === 0) {
          return <span className="text-text-muted">₹0.00</span>;
        }
        return <span className="text-crimson font-medium">{formatCurrency(diff)}</span>;
      }
    },
    { 
      header: "Reason", 
      accessorKey: "description",
      className: "text-xs text-text-secondary min-w-[260px] whitespace-normal px-3 py-2",
      cell: (row: any) => row.description || row.title || "-"
    },
    { 
      header: "Suggested Action", 
      accessorKey: "suggested_action",
      className: "text-xs text-text-muted min-w-[170px] whitespace-nowrap px-3 py-2",
      cell: (row: any) => row.suggested_action || row.recommended_action || "Manual Review"
    },
    { 
      header: "Severity", 
      accessorKey: "severity",
      className: "whitespace-nowrap px-3 py-2",
      cell: (row: any) => (
        <StatusBadge 
          status={row.severity === "CRITICAL" || row.severity === "HIGH" ? "error" : row.severity === "MEDIUM" ? "warning" : "info"} 
          label={row.severity} 
        />
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-text-secondary">Overview of reconciliation status and financial metrics.</p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/reports" className={buttonVariants({ variant: "outline" })}>
            View Reports
          </Link>
          <Link href="/upload" className={buttonVariants({ variant: "default", className: "bg-brand hover:bg-brand-hover text-white" })}>
            New Reconciliation
          </Link>
        </div>
      </div>

      {isEmptyState && (
        <div className="rounded-xl border border-brand/20 bg-brand-subtle/30 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-sm">
          <div>
            <h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
              <Upload className="h-5 w-5 text-brand" />
              No Reconciliation Data Available
            </h2>
            <p className="text-sm text-text-secondary mt-1 max-w-2xl">
              No reconciliation has been performed yet. Upload a dataset or click <strong>Use Demo Dataset</strong> to run the automated reconciliation engine.
            </p>
          </div>
          <div className="flex items-center gap-3 w-full md:w-auto">
            <Link href="/upload" className={buttonVariants({ variant: "outline", className: "bg-bg-surface w-full md:w-auto" })}>
              Upload Files
            </Link>
            <Button 
              onClick={handleUseDemoDataset} 
              disabled={isDemoLoading} 
              className="bg-brand text-white hover:bg-brand-hover w-full md:w-auto"
            >
              {isDemoLoading ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <Sparkles className="h-4 w-4 mr-2" />}
              Use Demo Dataset
            </Button>
          </div>
        </div>
      )}

      <DashboardAISummaryCard />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Transactions"
          value={metrics.total_transactions.toString()}
          icon={Activity}
          iconClassName="bg-brand-subtle text-brand"
          subtitle={`Bank Vol: ${formatCurrency(stats.total_amount_processed)}`}
        />

        <MetricCard
          title="Matched"
          value={metrics.matched_transactions.toString()}
          icon={CheckCircle2}
          iconClassName="bg-teal-subtle text-teal"
          subtitle={`Settlement Vol: ${formatCurrency(stats.matched_amount)}`}
        />

        <MetricCard
          title="Unmatched"
          value={metrics.unmatched_transactions.toString()}
          icon={AlertTriangle}
          iconClassName="bg-crimson-subtle text-crimson"
          subtitle={`Unmatched Vol: ${formatCurrency(stats.unmatched_amount)}`}
          className="[&_.text-2xl]:text-crimson"
        />
        
        <MetricCard
          title="Match Rate"
          value={`${metrics.match_rate.toFixed(1)}%`}
          icon={FileText}
          iconClassName="bg-amber-subtle text-amber"
          subtitle={`${metrics.total_exceptions} exceptions flagged`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-xl border border-border-default bg-bg-surface flex flex-col overflow-hidden shadow-sm">
          <div className="p-6 border-b border-border-default flex justify-between items-center">
            <div>
              <h3 className="font-semibold">Recent Exceptions</h3>
              <p className="text-sm text-text-secondary">Latest anomalies requiring review</p>
            </div>
            <Link href="/exceptions" className={buttonVariants({ variant: "outline", size: "sm" })}>
              View All
            </Link>
          </div>
          <div className="p-0">
            <DataTable 
              data={recentExceptions} 
              columns={columns as any}
              emptyMessage="No recent exceptions found. Upload a dataset or click Use Demo Dataset to begin."
            />
          </div>
        </div>
        
        {chartData.length > 0 ? (
          <ExceptionBarChart data={chartData} />
        ) : (
          <div className="rounded-xl border border-border-default bg-bg-surface flex flex-col items-center justify-center p-8 text-center min-h-[300px]">
             <CheckCircle2 className="h-8 w-8 text-teal mb-3 opacity-50" />
             <h3 className="font-medium text-text-primary">No Data Available</h3>
             <p className="text-sm text-text-secondary mt-1 max-w-xs">
               Upload a dataset or click <strong>Use Demo Dataset</strong> to generate reconciliation charts.
             </p>
          </div>
        )}
      </div>
    </div>
  );
}
