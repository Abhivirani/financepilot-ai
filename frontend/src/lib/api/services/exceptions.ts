import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const exceptionsService = {
  list: (params?: Record<string, any>) => 
    apiClient.get(endpoints.exceptions, { params }),
  
  exportCSV: () => {
    return apiClient.get(`${endpoints.exceptions}/export/csv`, { responseType: 'blob' });
  },

  autoResolve: () => {
    return apiClient.post(`${endpoints.exceptions}/auto-resolve`);
  }
};
