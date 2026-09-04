"use client";

import * as React from "react";
import { Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-text-secondary">Configure reconciliation rules and system preferences.</p>
      </div>
      
      <div className="rounded-xl border border-border-default bg-bg-surface overflow-hidden shadow-sm">
        <div className="p-6 border-b border-border-default">
          <h3 className="font-semibold text-lg text-text-primary">Matching Rules</h3>
          <p className="text-sm text-text-secondary mt-1">Configure tolerances for automatic reconciliation.</p>
        </div>
        
        <div className="p-6 space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Amount Tolerance ($)
              </label>
              <p className="text-xs text-text-secondary mb-2">Maximum allowed difference between matched records.</p>
              <Input type="number" defaultValue="0.05" className="max-w-xs bg-bg-surface-sunken" />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Date Tolerance (Days)
              </label>
              <p className="text-xs text-text-secondary mb-2">Maximum allowed days between bank settlement and gateway transaction.</p>
              <Input type="number" defaultValue="2" className="max-w-xs bg-bg-surface-sunken" />
            </div>
          </div>
        </div>
      </div>
      
      <div className="rounded-xl border border-border-default bg-bg-surface overflow-hidden shadow-sm">
        <div className="p-6 border-b border-border-default">
          <h3 className="font-semibold text-lg text-text-primary">System Preferences</h3>
          <p className="text-sm text-text-secondary mt-1">Manage global system settings.</p>
        </div>
        
        <div className="p-6 space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-primary mb-1">
                Default Currency
              </label>
              <select className="flex h-10 w-full max-w-xs items-center justify-between rounded-md border border-border-default bg-bg-surface-sunken px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand focus:border-transparent">
                <option value="usd">USD - US Dollar</option>
                <option value="eur">EUR - Euro</option>
                <option value="gbp">GBP - British Pound</option>
              </select>
            </div>
          </div>
        </div>
        
        <div className="p-6 bg-bg-surface-sunken border-t border-border-default flex justify-end">
          <Button className="bg-brand hover:bg-brand-hover text-white">
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>
    </div>
  );
}
