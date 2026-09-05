export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const endpoints = {
  health: '/health',
  dashboard: '/dashboard',
  upload: '/upload',
  uploadDemo: '/upload/demo',
  reconcile: '/reconcile',
  exceptions: '/exceptions',
  settings: '/settings',
  reports: '/reports',
  ai: {
    explain: '/ai/explain',
    chat: '/ai/chat',
    summarize: '/ai/summarize',
  }
} as const;
