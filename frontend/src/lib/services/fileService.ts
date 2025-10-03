/**
 * File operations API service.
 */

import { BaseApiService } from './baseApiService';

interface FileResponse {
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
}

interface CreateFileData {
  name: string;
  content?: string;
  team_id?: number;
}

interface UpdateFileData {
  name?: string;
  content?: string;
}

interface FileListResponse {
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
}

export class FileService extends BaseApiService {
  async getFile(fileId: string): Promise<FileResponse> {
    const response = await fetch(`${this.apiBase}/files/${fileId}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async updateFile(fileId: string, updates: UpdateFileData): Promise<FileResponse> {
    const response = await fetch(`${this.apiBase}/files/${fileId}`, {
      method: 'PATCH',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updates),
    });

    return this.handleResponse(response);
  }

  async createFile(data: CreateFileData): Promise<FileResponse> {
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

  async listFiles(): Promise<FileListResponse> {
    const response = await fetch(`${this.apiBase}/files`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }

  async getFileContent(fileId: string): Promise<{ content: string; name: string }> {
    const response = await fetch(`${this.apiBase}/files/${fileId}/content`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    return this.handleResponse(response);
  }
}

export const fileService = new FileService();