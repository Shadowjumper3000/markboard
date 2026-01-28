/**
 * Service registry for easy access to all API services.
 * Follows the Single Responsibility Principle by delegating to specific services.
 */

import { fileService } from './fileService';
import { teamService } from './teamService';
import { adminService } from './adminService';

export const apiServices = {
  files: fileService,
  teams: teamService,
  admin: adminService,
} as const;

// Legacy compatibility - re-export the old unified service
export { apiService } from '../api';

export * from './fileService';
export * from './teamService';
export * from './adminService';
export * from './baseApiService';