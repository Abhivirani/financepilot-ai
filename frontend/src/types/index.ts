export interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  iconClassName?: string;
  trend?: {
    value: string;
    isPositive: boolean;
    label: string;
  };
  subtitle?: string;
  className?: string;
}

export interface ChartCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}

export interface DataPoint {
  rule: string;
  count: number;
  color: string;
}

export interface ExceptionBarChartProps {
  data: DataPoint[];
  title?: string;
  description?: string;
}

export interface Exception {
  id: string;
  transaction_id: string;
  rule: string;
  severity: "critical" | "high" | "medium" | "low";
  status: "open" | "investigating" | "resolved";
  age: string;
}

export interface Batch {
  id: string;
  date: string;
  status: "completed" | "failed" | "running";
  records: number;
  exceptions: number;
}
