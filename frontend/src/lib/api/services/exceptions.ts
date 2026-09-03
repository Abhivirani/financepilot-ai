import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const exceptionsService = {
  list: (params?: Record<string, any>) => 
    apiClient.get(endpoints.exceptions, { params }),
};
