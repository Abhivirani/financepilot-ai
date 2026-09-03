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
  reply: string;
  suggested_questions: string[];
  source: "llm" | "cache" | "placeholder";
}

export interface SuggestedQuestion {
  id: string;
  text: string;
  category: "exception" | "report" | "general";
}

// ──────────────────────────────────────────────
// Exception Explanation
// ──────────────────────────────────────────────

export interface AIExplanation {
  explanation: string;
  confidence: ConfidenceLevel;
  suggested_actions: string[];
  source: "llm" | "cache" | "placeholder";
}

// ──────────────────────────────────────────────
// Report Summary
// ──────────────────────────────────────────────

export interface AIReportSummary {
  summary: string;
  key_findings: string[];
  source: "llm" | "cache" | "placeholder";
}
