"use client";

import * as React from "react";
import { SidebarNav } from "./SidebarNav";
import { TopBar } from "./TopBar";

interface AppShellProps {
  children: React.ReactNode;
  topBarContent?: React.ReactNode;
}

export function AppShell({ children, topBarContent }: AppShellProps) {
  return (
    <div className="flex h-screen overflow-hidden bg-bg-app">
      <SidebarNav />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar>{topBarContent}</TopBar>
        <main className="flex-1 overflow-y-auto p-6">
          <div className="mx-auto max-w-7xl w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
