"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  UploadCloud, 
  ArrowLeftRight, 
  AlertTriangle, 
  FileBarChart2, 
  Settings,
  Search,
  ChevronLeft,
  ChevronRight,
  Sparkles
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useSidebarStore } from "@/stores/useSidebarStore";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "./ThemeToggle";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Upload & Reconcile", href: "/upload", icon: UploadCloud },
  { name: "Exceptions", href: "/exceptions", icon: AlertTriangle, badge: 12 },
  { name: "AI Assistant", href: "/ai", icon: Sparkles },
  { name: "Reports", href: "/reports", icon: FileBarChart2 },
];

export function SidebarNav() {
  const pathname = usePathname();
  const { collapsed, toggle } = useSidebarStore();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredNavItems = navItems.filter(item => 
    item.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-border-default bg-bg-surface transition-all duration-200 h-screen sticky top-0",
        collapsed ? "w-16" : "w-60"
      )}
    >
      <div className="flex h-14 items-center justify-between px-3 border-b border-border-default">
        <div className="flex items-center gap-2 overflow-hidden whitespace-nowrap">
          <div className="h-8 w-8 rounded-md bg-brand text-primary-foreground flex items-center justify-center shrink-0 font-bold">
            FP
          </div>
          {!collapsed && <span className="font-semibold">FinancePilot</span>}
        </div>
        <button
          onClick={toggle}
          className="text-text-secondary hover:text-text-primary rounded-md p-1"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      <div className="px-3 py-2">
        <div className={cn(
          "flex items-center gap-2 w-full rounded-md border border-border-default bg-bg-surface-sunken px-2 py-1.5 text-sm text-text-secondary transition-colors focus-within:border-brand focus-within:text-text-primary",
          collapsed ? "justify-center px-0 cursor-pointer hover:text-text-primary" : ""
        )}
        onClick={() => collapsed && toggle()}
        >
          <Search size={16} className="shrink-0" />
          {!collapsed && (
            <input
              type="text"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-transparent border-none outline-none text-text-primary placeholder:text-text-muted text-sm"
            />
          )}
        </div>
      </div>

      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
        {filteredNavItems.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors relative",
                isActive
                  ? "bg-brand-subtle text-brand border-l-2 border-brand"
                  : "text-text-secondary hover:bg-bg-surface-sunken hover:text-text-primary",
                collapsed ? "justify-center px-0 border-l-0" : ""
              )}
              title={collapsed ? item.name : undefined}
            >
              <item.icon size={20} className={cn("shrink-0", isActive ? "text-brand" : "text-text-secondary")} />
              {!collapsed && (
                <span className="flex-1 overflow-hidden whitespace-nowrap">
                  {item.name}
                </span>
              )}
              {!collapsed && item.badge && (
                <Badge variant="destructive" className="bg-signal-amber text-primary-foreground border-transparent rounded-full px-1.5 font-mono text-xs">
                  {item.badge}
                </Badge>
              )}
              {collapsed && item.badge && isActive === false && (
                <div className="absolute right-2 top-2 h-2 w-2 rounded-full bg-signal-amber" />
              )}
            </Link>
          );
        })}
        {filteredNavItems.length === 0 && !collapsed && (
          <div className="text-center text-sm text-text-muted mt-4">
            No results found
          </div>
        )}
      </nav>

      <div className="p-3 border-t border-border-default space-y-2">
        <Link
          href="/settings"
          className={cn(
            "group flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-text-secondary hover:bg-bg-surface-sunken hover:text-text-primary transition-colors",
            pathname.startsWith("/settings") ? "bg-brand-subtle text-brand" : "",
            collapsed ? "justify-center px-0" : ""
          )}
          title={collapsed ? "Settings" : undefined}
        >
          <Settings size={20} className="shrink-0" />
          {!collapsed && <span>Settings</span>}
        </Link>
        <div className={cn("flex items-center", collapsed ? "justify-center" : "px-3")}>
          <ThemeToggle />
        </div>
      </div>

      <div className="p-3 border-t border-border-default">
        <div className={cn("flex items-center gap-3", collapsed ? "justify-center" : "")}>
          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-brand-subtle text-brand text-xs font-semibold">PM</AvatarFallback>
          </Avatar>
          {!collapsed && (
            <div className="flex flex-col overflow-hidden">
              <span className="text-sm font-medium text-text-primary truncate">Priya Menon</span>
              <span className="text-xs text-text-secondary truncate">priya@acme.com</span>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
