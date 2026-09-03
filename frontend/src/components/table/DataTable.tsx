"use client";

import * as React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

interface Column<T> {
  header: string;
  accessorKey?: keyof T;
  cell?: (item: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  isLoading?: boolean;
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
}

export function DataTable<T>({
  data,
  columns,
  isLoading,
  onRowClick,
  emptyMessage = "No results found.",
}: DataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="rounded-md border border-border-default overflow-hidden">
        <Table>
          <TableHeader className="bg-bg-surface-sunken">
            <TableRow>
              {columns.map((col, i) => (
                <TableHead key={i} className={col.className}>
                  {col.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody className="bg-bg-surface">
            {Array.from({ length: 5 }).map((_, rowIndex) => (
              <TableRow key={rowIndex}>
                {columns.map((col, colIndex) => (
                  <TableCell key={colIndex} className={col.className}>
                    <Skeleton className="h-4 w-full max-w-[120px]" />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-border-default overflow-hidden">
      <Table>
        <TableHeader className="bg-bg-surface-sunken">
          <TableRow className="border-border-default hover:bg-transparent">
            {columns.map((col, i) => (
              <TableHead key={i} className={cn("font-medium text-text-secondary whitespace-nowrap", col.className)}>
                {col.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody className="bg-bg-surface">
          {data.length ? (
            data.map((row, rowIndex) => (
              <TableRow
                key={rowIndex}
                onClick={() => onRowClick?.(row)}
                className={cn(
                  "border-border-default group transition-colors",
                  onRowClick ? "cursor-pointer hover:bg-bg-surface-sunken" : "hover:bg-transparent"
                )}
              >
                {columns.map((col, colIndex) => (
                  <TableCell key={colIndex} className={cn("text-text-primary py-3", col.className)}>
                    {col.cell ? col.cell(row) : (row as any)[col.accessorKey as string]}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center text-text-secondary">
                {emptyMessage}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
