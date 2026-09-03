import * as React from "react";
import { AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ title = "Something went wrong", message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-lg border border-border-default bg-crimson-subtle/50">
      <div className="relative flex h-16 w-16 items-center justify-center rounded-full bg-crimson-subtle mb-4">
        <div className="absolute inset-0 rounded-full bg-crimson opacity-20 blur-lg"></div>
        <AlertCircle className="h-8 w-8 text-crimson relative z-10" />
      </div>
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      <p className="text-sm text-text-secondary mb-4 max-w-md">
        {message}
      </p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" className="border-border-strong">
          Try again
        </Button>
      )}
    </div>
  );
}
