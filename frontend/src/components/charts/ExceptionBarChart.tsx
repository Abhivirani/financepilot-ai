"use client";

import React, { useMemo } from "react";
import { ChartCard } from "../shared/ChartCard";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Cell
} from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2 } from "lucide-react";

interface DataPoint {
  rule: string;
  count: number;
  color: string;
}

interface ExceptionBarChartProps {
  data: DataPoint[];
  title?: string;
  description?: string;
  isLoading?: boolean;
}

export function ExceptionBarChart({ 
  data, 
  title = "Exception Breakdown", 
  description = "Distribution by rule type",
  isLoading = false
}: ExceptionBarChartProps) {
  // Step 9 & 13: Data validation, deduping, and memoization
  const processedData = useMemo(() => {
    if (!data || !Array.isArray(data)) return [];
    
    const ruleMap = new Map<string, DataPoint>();
    
    data.forEach(item => {
      if (!item || !item.rule) return;
      
      const cleanRule = String(item.rule).trim();
      if (!cleanRule) return;
      
      if (ruleMap.has(cleanRule)) {
        const existing = ruleMap.get(cleanRule)!;
        ruleMap.set(cleanRule, {
          ...existing,
          count: existing.count + (item.count || 0)
        });
      } else {
        ruleMap.set(cleanRule, {
          rule: cleanRule,
          count: item.count || 0,
          color: item.color || "var(--brand)"
        });
      }
    });
    
    return Array.from(ruleMap.values());
  }, [data]);

  // Step 11: Loading state
  if (isLoading) {
    return (
      <ChartCard title={title} description={description} className="h-[400px]">
        <div className="w-full h-full min-h-[300px] flex items-end justify-between px-4 pb-8 pt-8 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="flex-1 w-full" style={{ height: `${Math.random() * 60 + 20}%` }} />
          ))}
        </div>
      </ChartCard>
    );
  }

  // Step 10: Empty state
  if (processedData.length === 0) {
    return (
      <ChartCard title={title} description={description} className="h-[400px]">
        <div className="w-full h-full min-h-[300px] flex flex-col items-center justify-center text-text-secondary">
          <CheckCircle2 className="h-8 w-8 text-teal mb-3 opacity-50" />
          <h3 className="font-medium text-text-primary">No exception data available</h3>
          <p className="text-sm text-text-secondary mt-1">Your data is perfectly reconciled.</p>
        </div>
      </ChartCard>
    );
  }

  const totalExceptions = processedData.reduce((sum, item) => sum + item.count, 0);

  // Step 6: Add tooltips
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      const percent = totalExceptions > 0 
        ? ((dataPoint.count / totalExceptions) * 100).toFixed(1) 
        : "0.0";
        
      return (
        <div className="bg-bg-surface border border-border-default p-3 rounded-lg shadow-md text-sm z-50">
          <p className="font-semibold mb-2 text-text-primary border-b border-border-default pb-1">
            {dataPoint.rule}
          </p>
          <div className="flex justify-between gap-6 text-text-secondary mb-1">
            <span>Count:</span>
            <span className="font-medium text-text-primary">{dataPoint.count}</span>
          </div>
          <div className="flex justify-between gap-6 text-text-secondary">
            <span>Percentage:</span>
            <span className="font-medium text-text-primary">{percent}%</span>
          </div>
        </div>
      );
    }
    return null;
  };

  // Step 4 & 5: Responsive container, rotate labels, prevent overflow
  // Step 7: Adjusted margins so labels are not cut
  return (
    <ChartCard title={title} description={description} className="h-[400px]">
      <div className="w-full h-[320px] mt-2 relative">
        <ResponsiveContainer width="99%" height={320}>
          <BarChart
            data={processedData}
            margin={{ top: 20, right: 20, left: -20, bottom: 80 }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-default)" />
            <XAxis 
              dataKey="rule" 
              tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--border-default)" }}
              interval={0}
              angle={-45}
              textAnchor="end"
              height={70}
              tickMargin={10}
            />
            <YAxis 
              tick={{ fontSize: 11, fill: "var(--text-secondary)" }}
              tickLine={false}
              axisLine={false}
              allowDecimals={false}
            />
            <Tooltip 
              content={<CustomTooltip />} 
              cursor={{ fill: 'var(--bg-surface-hover)' }}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {processedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </ChartCard>
  );
}
