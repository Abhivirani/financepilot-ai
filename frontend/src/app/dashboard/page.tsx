"use client";

import { useDashboard } from "@/hooks/useApi";
import { MetricCardSkeleton, ChartCardSkeleton } from "@/components/shared/LoadingSkeletons";
import { ErrorState } from "@/components/shared/ErrorState";
import { MetricCard } from "@/components/shared/MetricCard";
import { Activity, AlertTriangle, FileText, CheckCircle2 } from "lucide-react";
import { Button, buttonVariants } from "@/components/ui/button";
import Link from "next/link";
import { StatusBadge } from "@/components/table/StatusBadge";
import { DataTable } from "@/components/table/DataTable";
import { ExceptionBarChart } from "@/components/charts/ExceptionBarChart";
import { format } from "date-fns";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  const { data, isLoading, isError, refetch } = useDashboard();

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="text-text-secondary">Overview of reconciliation status</p>
        </div>
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
    return (
      <div className="mt-12">
        <ErrorState 
          title="Failed to load dashboard" 
          message="There was a problem communicating with the backend API." 
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
    currency: "USD",
  };

  const metrics = data?.metrics || {
    match_rate: 0,
    total_exceptions: 0,
    total_transactions: 0
  };

  const recentExceptions = data?.recent_exceptions || [];
  const ruleDistribution = data?.rule_distribution || [];

  const chartData = ruleDistribution.map((item: any, i: number) => {
    const colors = ["var(--crimson)", "var(--amber)", "var(--brand)", "var(--text-disabled)"];
    return {
      rule: item.rule_type,
      count: item.count,
      color: colors[i % colors.length]
    };
  });

  const columns = [
    { header: "Exception ID", accessorKey: "exception_id", className: "font-mono text-xs max-w-[120px] truncate" },
    { header: "Rule Type", accessorKey: "rule_type", className: "font-medium" },
    { 
      header: "Date", 
      accessorKey: "created_at", 
      cell: (row: any) => format(new Date(row.created_at), "MMM d, HH:mm")
    },
    { 
      header: "Amount", 
      accessorKey: "amount", 
      className: "text-right font-mono",
      cell: (row: any) => `$${row.amount.toLocaleString('en-US', {minimumFractionDigits: 2})}`
    },
    { 
      header: "Severity", 
      accessorKey: "severity",
      cell: (row: any) => (
        <StatusBadge 
          status={row.severity === "CRITICAL" ? "error" : row.severity === "HIGH" ? "warning" : "neutral"} 
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Processed"
          value={`$${stats.total_amount_processed.toLocaleString('en-US', {minimumFractionDigits: 2})}`}
          icon={Activity}
          iconClassName="bg-brand-subtle text-brand"
          subtitle={`${metrics.total_transactions} transactions`}
        />

        <MetricCard
          title="Matched"
          value={`$${stats.matched_amount.toLocaleString('en-US', {minimumFractionDigits: 2})}`}
          icon={CheckCircle2}
          iconClassName="bg-teal-subtle text-teal"
          subtitle={`${metrics.match_rate.toFixed(1)}% match rate`}
        />

        <MetricCard
          title="Exceptions"
          value={`$${stats.unmatched_amount.toLocaleString('en-US', {minimumFractionDigits: 2})}`}
          icon={AlertTriangle}
          iconClassName="bg-crimson-subtle text-crimson"
          trend={{ value: "", isPositive: false, label: `${metrics.total_exceptions} cases found` }}
          className="[&_.text-2xl]:text-crimson"
        />
        
        <MetricCard
          title="Reports Generated"
          value="12"
          icon={FileText}
          iconClassName="bg-amber-subtle text-amber"
          subtitle="This month"
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
              emptyMessage="No recent exceptions found."
            />
          </div>
        </div>
        
        {chartData.length > 0 ? (
          <ExceptionBarChart data={chartData} />
        ) : (
          <div className="rounded-xl border border-border-default bg-bg-surface flex flex-col items-center justify-center p-8 text-center min-h-[300px]">
             <CheckCircle2 className="h-8 w-8 text-teal mb-3 opacity-50" />
             <h3 className="font-medium text-text-primary">No Exceptions</h3>
             <p className="text-sm text-text-secondary mt-1">Your data is perfectly reconciled.</p>
          </div>
        )}
      </div>
    </div>
  );
}
