import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const reportsService = {
  list: () => apiClient.get(endpoints.reports),
};
