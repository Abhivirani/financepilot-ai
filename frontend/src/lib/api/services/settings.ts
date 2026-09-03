import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const settingsService = {
  get: () => apiClient.get(endpoints.settings),
  update: (data: Record<string, any>) => apiClient.patch(endpoints.settings, data),
};
