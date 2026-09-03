import { apiClient } from '../axios';
import { endpoints } from '../endpoints';
import type { AIExplainResponseData, AIDashboardSummaryResponseData, ChatResponse, AIReportSummary } from '@/types/ai';

export const aiService = {
  /**
   * Explain a specific reconciliation exception.
   * Currently returns the backend placeholder; will return Claude response
   * once the AI Copilot is activated.
   */
  explain: (exceptionId: string): Promise<{ data: AIExplainResponseData }> => 
    apiClient.post(endpoints.ai.explain, { exception_id: exceptionId }),

  /**
   * Generate an executive summary of the current dashboard metrics.
   */
  getDashboardSummary: (): Promise<{ data: AIDashboardSummaryResponseData }> =>
    apiClient.post('/ai/dashboard-summary', {}),

  /**
   * Free-form chat with the AI assistant.
   */
  chat: (message: string): Promise<{ data: ChatResponse }> =>
    apiClient.post('/ai/chat', { message }),

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
