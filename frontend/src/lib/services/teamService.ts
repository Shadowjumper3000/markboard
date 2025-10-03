/**
 * Team operations API service.
 */

import { BaseApiService } from './baseApiService';

interface Team {
  id: number;
  name: string;
  description: string;
  owner_id: number;
  file_count?: number;
  member_count?: number;
  role?: string;
  created_at: string;
}

interface TeamUser {
  id: number;
  email: string;
  is_admin?: boolean;
  created_at?: string;
  last_login?: string | null;
  role?: string;
}

interface CreateTeamData {
  name: string;
  description?: string;
}

export class TeamService extends BaseApiService {
  async listTeams(): Promise<{ teams: Team[] }> {
    const response = await fetch(`${this.apiBase}/teams`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async createTeam(data: CreateTeamData): Promise<Team> {
    const response = await fetch(`${this.apiBase}/teams`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return this.handleResponse(response);
  }

  async joinTeam(teamId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}/join`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getAvailableTeams(): Promise<{ teams: Team[] }> {
    const response = await fetch(`${this.apiBase}/teams/available`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async leaveTeam(teamId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}/leave`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async disbandTeam(teamId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}`, {
      method: 'DELETE',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getTeamUsers(teamId: number): Promise<{ users: TeamUser[] }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}/users`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });
    
    return this.handleResponse(response);
  }

  async kickUserFromTeam(teamId: number, userId: number): Promise<{ message: string }> {
    const response = await fetch(`${this.apiBase}/teams/${teamId}/kick`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ user_id: userId }),
    });
    
    return this.handleResponse(response);
  }

  async getUserTeamCount(): Promise<{ count: number }> {
    const response = await fetch(`${this.apiBase}/teams/count`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }
}

export const teamService = new TeamService();