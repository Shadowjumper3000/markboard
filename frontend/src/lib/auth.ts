import Cookies from 'js-cookie';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
}

// Backend API base URL
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const authService = {
  async login(email: string, password: string): Promise<User> {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || error.message || 'Login failed');
    }

    const data = await response.json();
    const token = data.token; // Fixed: data.token instead of data.data.token
    
    // Store JWT token in both cookie and localStorage for compatibility
    Cookies.set('auth-token', token, { expires: 7 });
    localStorage.setItem('token', token);
    
    // Decode user info from token or fetch user details
    const userResponse = await fetch(`${API_BASE}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (userResponse.ok) {
      const userData = await userResponse.json();
      return {
        id: userData.id.toString(), // Fixed: userData.id instead of userData.data.id
        email: userData.email, // Fixed: userData.email instead of userData.data.email
        name: userData.name || userData.email.split('@')[0],
        role: userData.is_admin ? 'admin' : 'user', // Fixed: userData.is_admin instead of userData.data.is_admin
        createdAt: userData.created_at, // Fixed: userData.created_at instead of userData.data.created_at
      };
    }
    
    // Fallback: create user object from login response
    return {
      id: data.user_id.toString(), // Fixed: data.user_id instead of data.data.user_id
      email: data.email, // Fixed: data.email instead of data.data.email
      name: data.email.split('@')[0],
      role: data.is_admin ? 'admin' : 'user', // Fixed: data.is_admin instead of data.data.is_admin
      createdAt: new Date().toISOString(),
    };
  },

  async signup(email: string, password: string, name: string): Promise<User> {
    const response = await fetch(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || error.message || 'Signup failed');
    }

    const data = await response.json();
    
    // Auto-login after successful signup
    return this.login(email, password);
  },

  logout(): void {
    Cookies.remove('auth-token');
    localStorage.removeItem('token');
  },

  getCurrentUser(): User | null {
    const token = Cookies.get('auth-token') || localStorage.getItem('token');
    if (!token) return null;
    
    try {
      // Decode JWT token to get user info
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      
      const payload = JSON.parse(jsonPayload);
      
      // Check if token is expired
      if (payload.exp && payload.exp < Date.now() / 1000) {
        this.logout();
        return null;
      }
      
      return {
        id: payload.user_id?.toString() || '1',
        email: payload.email || 'user@example.com',
        name: payload.name || payload.email?.split('@')[0] || 'User',
        role: payload.is_admin ? 'admin' : 'user',
        createdAt: new Date(payload.iat * 1000).toISOString(),
      };
    } catch (error) {
      // If token is invalid, clear it
      this.logout();
      return null;
    }
  },

  isAuthenticated(): boolean {
    return !!(Cookies.get('auth-token') || localStorage.getItem('token'));
  }
};