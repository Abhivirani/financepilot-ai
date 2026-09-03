import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const uploadService = {
  uploadFiles: (formData: FormData) => 
    apiClient.post(endpoints.upload, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};
