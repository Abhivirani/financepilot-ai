import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const healthService = {
  check: () => apiClient.get(endpoints.health),
};
