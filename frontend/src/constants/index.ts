export const FILE_CONSTRAINTS = {
  MAX_NAME_LENGTH: 100, // More reasonable than 20
  MAX_SIZE_MB: 10,
  MAX_CONTENT_LENGTH: 2000,
} as const;

export const TOAST_CONFIG = {
  REMOVE_DELAY: 5000, // 5 seconds instead of 16+ minutes
  LIMIT: 3,
} as const;

export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  TIMEOUT: 10000,
} as const;