"use client";

import * as React from "react";
import { ChartCard } from "../shared/ChartCard";

interface DataPoint {
  rule: string;
  count: number;
  color: string;
}

interface ExceptionBarChartProps {
  data: DataPoint[];
  title?: string;
  description?: string;
}

export function ExceptionBarChart({ 
  data, 
  title = "Exception Breakdown", 
  description = "Distribution by rule type" 
}: ExceptionBarChartProps) {
  const maxCount = Math.max(...data.map(d => d.count), 1);

  return (
    <ChartCard title={title} description={description} className="h-[400px]">
      <div className="w-full h-full min-h-[200px] flex items-end justify-between px-4 pb-2 pt-8 gap-4 border-b border-border-default relative">
        {/* Y Axis Grid Lines */}
        <div className="absolute inset-0 flex flex-col justify-between pb-8 pt-8 z-0">
          {[0, 1, 2, 3, 4].map((i) => (
            <div key={i} className="w-full border-t border-dashed border-border-default flex-1 relative">
              <span className="absolute -left-6 -top-2.5 text-xs text-text-secondary">
                {Math.round(maxCount - (i * maxCount / 4))}
              </span>
            </div>
          ))}
        </div>

        {/* Bars */}
        {data.map((item, idx) => (
          <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full relative z-10 group">
            <div className="w-full max-w-[48px] bg-bg-surface-sunken rounded-t flex flex-col justify-end group-hover:bg-bg-surface-hover transition-colors">
              <div 
                className="w-full rounded-t transition-all duration-500 ease-out" 
                style={{ 
                  height: `${(item.count / maxCount) * 100}%`,
                  backgroundColor: item.color 
                }}
              ></div>
            </div>
            <div className="absolute -bottom-8 text-xs text-text-secondary whitespace-nowrap text-center w-full">
              {item.rule}
            </div>
          </div>
        ))}
      </div>
    </ChartCard>
  );
}
