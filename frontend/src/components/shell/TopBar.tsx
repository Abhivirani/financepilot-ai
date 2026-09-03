"use client";

import * as React from "react";
import { ChevronRight } from "lucide-react";
import { usePathname } from "next/navigation";

interface TopBarProps {
  children?: React.ReactNode;
}

export function TopBar({ children }: TopBarProps) {
  const pathname = usePathname();
  
  // Basic breadcrumb generation
  const paths = pathname.split('/').filter(Boolean);
  const breadcrumbs = paths.map((path, index) => {
    const isLast = index === paths.length - 1;
    const formattedPath = path.charAt(0).toUpperCase() + path.slice(1).replace(/-/g, ' ');
    return { name: formattedPath, isLast };
  });

  return (
    <header className="flex h-14 items-center justify-between border-b border-border-default bg-bg-surface px-6 sticky top-0 z-10">
      <div className="flex items-center text-sm">
        {breadcrumbs.length > 0 ? (
          <nav className="flex items-center text-text-secondary">
            {breadcrumbs.map((crumb, idx) => (
              <React.Fragment key={idx}>
                {idx > 0 && <ChevronRight className="mx-2 h-4 w-4" />}
                <span className={crumb.isLast ? "font-medium text-text-primary" : ""}>
                  {crumb.name}
                </span>
              </React.Fragment>
            ))}
          </nav>
        ) : (
          <span className="font-medium text-text-primary">FinancePilot AI</span>
        )}
      </div>
      <div className="flex items-center gap-3">
        {children}
      </div>
    </header>
  );
}
