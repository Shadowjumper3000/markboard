/**
 * Base API service with common functionality.
 */

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export abstract class BaseApiService {
  protected readonly apiBase: string;

  constructor() {
    this.apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
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
}