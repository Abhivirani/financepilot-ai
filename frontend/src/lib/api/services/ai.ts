import { apiClient } from '../axios';
import { endpoints } from '../endpoints';
import type { AIExplainResponseData, AIDashboardSummaryResponseData, ChatResponse, AIReportSummary, AIExecutiveReportResponseData } from '@/types/ai';

export const aiService = {
  /**
   * Explain a specific reconciliation exception.
   * Sends a chat message to the AI copilot and returns the Gemini response
   * once the AI Copilot is activated.
   */
  explain: (exceptionId: string): Promise<AIExplainResponseData> => 
    apiClient.post(endpoints.ai.explain, { exception_id: exceptionId }),

  /**
   * Generate an executive summary of the current dashboard metrics.
   */
  getDashboardSummary: (): Promise<AIDashboardSummaryResponseData> =>
    apiClient.post('/ai/dashboard-summary', {}),

  /**
   * Free-form chat with the AI assistant.
   */
  chat: (message: string): Promise<ChatResponse> =>
    apiClient.post('/ai/chat', { message }),

  /**
   * Generate an AI executive report.
   */
  generateExecutiveReport: (): Promise<AIExecutiveReportResponseData> =>
    apiClient.post('/ai/executive-report', {}),
};
