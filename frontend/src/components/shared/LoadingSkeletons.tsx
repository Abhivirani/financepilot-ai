import { Skeleton } from "@/components/ui/skeleton";

export function MetricCardSkeleton() {
  return (
    <div className="rounded-xl border border-border-default bg-bg-surface p-6">
      <Skeleton className="h-4 w-1/2 mb-4" />
      <Skeleton className="h-8 w-2/3 mb-2" />
      <Skeleton className="h-4 w-1/3" />
    </div>
  );
}

export function ChartCardSkeleton() {
  return (
    <div className="rounded-xl border border-border-default bg-bg-surface p-6 h-[400px] flex flex-col">
      <Skeleton className="h-5 w-1/4 mb-6" />
      <Skeleton className="flex-1 w-full" />
    </div>
  );
}
