/**
 * Shared type definitions for the AI Copilot feature.
 *
 * These types mirror the backend Pydantic schemas and are used across
 * components, hooks, and API services.
 */

// ──────────────────────────────────────────────
// Enums / Literals
// ──────────────────────────────────────────────

export type ConfidenceLevel = "high" | "medium" | "low";

// ──────────────────────────────────────────────
// Chat
// ──────────────────────────────────────────────

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  confidence?: ConfidenceLevel;
  suggestedActions?: string[];
  source?: "llm" | "cache" | "placeholder";
  timestamp?: string;
}

export interface ChatResponse {
  answer: string;
  confidence: number;
  latency_ms: number;
  generated_at: string;
}

export interface SuggestedQuestion {
  id: string;
  text: string;
  category: "exception" | "report" | "general";
}

// ──────────────────────────────────────────────
// Exception Explanation
// ──────────────────────────────────────────────

export interface AIExplainResponseData {
  summary: string;
  markdown: string;
  confidence: number;
  latency_ms: number;
}

export interface AIDashboardSummaryResponseData {
  summary: string;
  markdown: string;
  confidence: number;
  latency_ms: number;
  generated_at: string;
}

// ──────────────────────────────────────────────
// Report Summary
// ──────────────────────────────────────────────

export interface AIReportSummary {
  summary: string;
  key_findings: string[];
  source: "llm" | "cache" | "placeholder";
}
