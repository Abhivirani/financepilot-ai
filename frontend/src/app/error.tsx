"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error("Application error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[400px] w-full text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-crimson-subtle mb-6">
        <AlertCircle className="h-8 w-8 text-crimson" />
      </div>
      <h2 className="text-2xl font-semibold tracking-tight text-text-primary mb-2">Something went wrong!</h2>
      <p className="text-text-secondary max-w-md mb-8">
        We encountered an unexpected error while trying to process your request.
      </p>
      <div className="flex gap-4">
        <Button onClick={() => window.location.reload()} variant="outline">
          Reload Page
        </Button>
        <Button onClick={() => reset()} className="bg-brand hover:bg-brand-hover text-white">
          Try Again
        </Button>
      </div>
    </div>
  );
}
