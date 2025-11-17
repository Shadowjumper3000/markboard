/**
 * Legacy API service - DEPRECATED
 * Use the specific services from lib/services/ instead:
 * - fileService for file operations
 * - teamService for team operations  
 * - adminService for admin operations
 * 
 * This class is kept for backwards compatibility.
 */

import { BaseApiService } from './services/baseApiService';



interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

class ApiService extends BaseApiService {
  async kickUserFromTeam(teamId: number, userId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}/kick`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ user_id: userId }),
    });
    return this.handleResponse(response);
  }
  // Get users of a team
  async getTeamUsers(teamId: number): Promise<{
    users: Array<{
      id: number;
      email: string;
      is_admin?: boolean;
      created_at?: string;
      last_login?: string | null;
      role?: string;
    }>;
  }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}/users`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });
    return this.handleResponse(response);
  }
  protected getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    };
  }

  protected async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: 'Request failed' }));
      throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    if (data.success === false) {
      throw new Error(data.message || 'Request failed');
    }

    return data;
  }

  // File operations
  async getFile(fileId: string): Promise<{
    id: number;
    name: string;
    content: string;
    file_size: number;
    size_formatted: string;
    mime_type: string;
    owner_id: number;
    team_id: number | null;
    created_at: string;
    updated_at: string;
  }> {
    const response = await fetch(`${this.apiBase}/files/${fileId}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async updateFile(fileId: string, updates: {
    name?: string;
    content?: string;
  }): Promise<{
    id: number;
    name: string;
    owner_id: number;
    team_id: number | null;
    created_at: string;
    updated_at: string;
  }> {
    const response = await fetch(`${this.apiBase}/files/${fileId}`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updates),
    });

    return this.handleResponse(response);
  }

  async createFile(data: {
    name: string;
    content?: string;
    team_id?: number;
  }): Promise<{
    id: number;
    name: string;
    file_size: number;
    size_formatted: string;
    mime_type: string;
    owner_id: number;
    team_id: number | null;
    created_at: string;
    updated_at: string;
  }> {
    const response = await fetch(`${this.apiBase}/files`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  }

  async deleteFile(fileId: string): Promise<void> {
    const response = await fetch(`${this.apiBase}/files/${fileId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    await this.handleResponse(response);
  }

  async listFiles(): Promise<{
    files: Array<{
      id: number;
      name: string;
      file_size: number;
      size_formatted: string;
      mime_type: string;
      owner_id: number;
      team_id: number | null;
      created_at: string;
      updated_at: string;
    }>;
  }> {
    const response = await fetch(`${this.apiBase}/files`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  // Team operations
  async listTeams(): Promise<{
    teams: Array<{
      id: number;
      name: string;
      description: string;
      owner_id: number;
      file_count?: number;
      member_count?: number;
      role?: string;
      created_at: string;
    }>;
  }> {
    const response = await fetch(`${this.apiBase}/teams`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async createTeam(data: {
    name: string;
    description?: string;
  }): Promise<{
    id: number;
    name: string;
    description: string;
    owner_id: number;
    created_at: string;
  }> {
    const response = await fetch(`${this.apiBase}/teams`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  }

  async joinTeam(teamId: number): Promise<{
    message: string;
  }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}/join`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getAvailableTeams(): Promise<{
    teams: Array<{
      id: number;
      name: string;
      description: string;
      owner_id: number;
      file_count?: number;
      member_count?: number;
      created_at: string;
    }>;
  }> {
    const response = await fetch(`${this.apiBase}/teams/available`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async leaveTeam(teamId: number): Promise<{
    message: string;
  }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}/leave`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async disbandTeam(teamId: number): Promise<{
    message: string;
  }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  // Admin operations
  async getAdminUsers(): Promise<{
    users: Array<{
      id: number;
      email: string;
      is_admin: boolean;
      file_count: number;
      team_count: number;
      status: string;
      last_active: string;
      created_at: string;
      last_login: string | null;
    }>;
  }> {
    const response = await fetch(`${this.apiBase}/admin/users`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getAdminStats(): Promise<{
    totalUsers: number;
    activeUsers: number;
    totalFiles: number;
    totalTeams: number;
    recentActivity: number;
  }> {
    const response = await fetch(`${this.apiBase}/admin/stats`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getAdminTeams(): Promise<{
    teams: Array<{
      id: number;
      name: string;
      description: string;
      owner_id: number;
      owner_email: string;
      file_count: number;
      member_count: number;
      created_at: string;
    }>;
  }> {
    const response = await fetch(`${this.apiBase}/admin/teams`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getAdminActivity(limit?: number): Promise<{
    activities: Array<{
      id: number;
      user_id: number;
      action: string;
      resource_type: string;
      resource_id: number | null;
      details: string;
      created_at: string;
      user_email?: string;
    }>;
  }> {
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

  async getUserTeamCount(): Promise<{
    count: number;
  }> {
    const response = await fetch(`${this.apiBase}/teams/count`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }
}

export const apiService = new ApiService();