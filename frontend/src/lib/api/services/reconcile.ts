import { apiClient } from '../axios';
import { endpoints } from '../endpoints';

export const reconcileService = {
  run: (batchId: string) => 
    apiClient.post(endpoints.reconcile, { batch_id: batchId }),
};
