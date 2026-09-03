import Link from "next/link";
import { FileQuestion } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[400px] w-full text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-bg-surface-sunken mb-6">
        <FileQuestion className="h-8 w-8 text-text-secondary" />
      </div>
      <h2 className="text-2xl font-semibold tracking-tight text-text-primary mb-2">Page Not Found</h2>
      <p className="text-text-secondary max-w-md mb-8">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <Link href="/dashboard" className={buttonVariants({ variant: "default", className: "bg-brand hover:bg-brand-hover text-white" })}>
        Return to Dashboard
      </Link>
    </div>
  );
}
