import * as React from "react";
import { LucideIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ icon: Icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-16 text-center rounded-lg border border-dashed border-border-strong bg-bg-surface">
      <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-bg-surface-sunken mb-6">
        <div className="absolute inset-0 rounded-full bg-brand-subtle opacity-50 blur-xl"></div>
        <Icon className="h-10 w-10 text-text-secondary relative z-10" />
      </div>
      <h3 className="text-xl font-semibold tracking-tight text-text-primary mb-2">{title}</h3>
      <p className="text-sm text-text-secondary mb-6 max-w-sm">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="default" className="bg-brand hover:bg-brand-hover text-white">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
