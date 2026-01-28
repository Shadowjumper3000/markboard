/**
 * Admin operations API service.
 */

import { BaseApiService } from './baseApiService';

interface AdminUser {
  id: number;
  email: string;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
}

interface AdminStats {
  totalUsers: number;
  activeUsers: number;
  totalFiles: number;
  recentActivity: number;
}

interface AdminActivity {
  id: number;
  user_id: number;
  action: string;
  resource_type: string;
  resource_id: number | null;
  details: string;
  created_at: string;
  user_email?: string;
}

export class AdminService extends BaseApiService {
  async getUsers(): Promise<{ users: AdminUser[] }> {
    const response = await fetch(`${this.apiBase}/admin/users`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getStats(): Promise<AdminStats> {
    const response = await fetch(`${this.apiBase}/admin/stats`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getActivity(limit?: number): Promise<{ activities: AdminActivity[] }> {
    const url = new URL(`${this.apiBase}/admin/activity`);
    if (limit) {
      url.searchParams.set('limit', limit.toString());
    }

    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }
}

export const adminService = new AdminService();