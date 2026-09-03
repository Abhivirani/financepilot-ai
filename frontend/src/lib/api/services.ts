import { healthService } from './services/health';
import { dashboardService } from './services/dashboard';
import { uploadService } from './services/upload';
import { reconcileService } from './services/reconcile';
import { exceptionsService } from './services/exceptions';
import { aiService } from './services/ai';
import { settingsService } from './services/settings';
import { reportsService } from './services/reports';

export const ApiService = {
  health: healthService,
  dashboard: dashboardService,
  upload: uploadService,
  reconcile: reconcileService,
  exceptions: exceptionsService,
  ai: aiService,
  settings: settingsService,
  reports: reportsService,
};
