import { apiClient } from '../axios';
import { endpoints } from '../endpoints';
import type { AIExplanation, ChatResponse, AIReportSummary } from '@/types/ai';

export const aiService = {
  /**
   * Explain a specific reconciliation exception.
   * Currently returns the backend placeholder; will return Claude response
   * once the AI Copilot is activated.
   */
  explain: (exceptionId: string) => 
    apiClient.post(endpoints.ai.explain, { exception_id: exceptionId }),

  /**
   * Free-form chat with the AI assistant.
   * Returns a mocked response until the backend chat endpoint is implemented.
   */
  chat: async (message: string, conversationHistory?: { role: string; content: string }[]): Promise<ChatResponse> => {
    // TODO: Replace with real API call when POST /ai/chat is implemented
    return {
      reply:
        "I'm currently in placeholder mode. Once Claude is connected, " +
        "I'll be able to answer questions about your reconciliation data, " +
        "explain specific exceptions, and suggest resolution strategies.",
      suggested_questions: [
        "What caused exception EX-1001?",
        "Summarise today's reconciliation results",
        "Which exceptions should I prioritise?",
      ],
      source: "placeholder",
    };
  },

  /**
   * Generate a natural-language summary of a reconciliation report.
   * Returns a mocked response until the backend endpoint is implemented.
   */
  summarizeReport: async (runId: string): Promise<AIReportSummary> => {
    // TODO: Replace with real API call when POST /ai/summarize is implemented
    return {
      summary:
        `Report for run ${runId}: This is a placeholder summary. ` +
        "Connect Claude to receive an AI-generated executive summary " +
        "covering match rates, exception trends, and recommended actions.",
      key_findings: [
        "Placeholder finding — connect Claude for real insights",
      ],
      source: "placeholder",
    };
  },
};
