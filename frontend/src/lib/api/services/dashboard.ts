import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const dashboardService = {
  get: () => apiClient.get(endpoints.dashboard),
};
