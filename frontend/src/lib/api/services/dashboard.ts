import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const dashboardService = {
  get: (runId?: string) => apiClient.get(endpoints.dashboard, { params: runId ? { run_id: runId } : {} }),
};
