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

// Mock JWT storage (replace with real backend integration)
export const authService = {
  async login(email: string, password: string): Promise<User> {
    // Mock login - replace with real API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    if (email === 'admin@example.com') {
      const user = {
        id: '1',
        email: 'admin@example.com',
        name: 'Admin User',
        role: 'admin' as const,
        createdAt: new Date().toISOString(),
      };
      Cookies.set('auth-token', 'mock-jwt-token', { expires: 7 });
      return user;
    }
    
    if (email.includes('@')) {
      const user = {
        id: Math.random().toString(36).substring(7),
        email,
        name: email.split('@')[0],
        role: 'user' as const,
        createdAt: new Date().toISOString(),
      };
      Cookies.set('auth-token', 'mock-jwt-token', { expires: 7 });
      return user;
    }
    
    throw new Error('Invalid credentials');
  },

  async signup(email: string, password: string, name: string): Promise<User> {
    // Mock signup - replace with real API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const user = {
      id: Math.random().toString(36).substring(7),
      email,
      name,
      role: 'user' as const,
      createdAt: new Date().toISOString(),
    };
    
    Cookies.set('auth-token', 'mock-jwt-token', { expires: 7 });
    return user;
  },

  logout(): void {
    Cookies.remove('auth-token');
  },

  getCurrentUser(): User | null {
    const token = Cookies.get('auth-token');
    if (!token) return null;
    
    // Mock user from token - replace with real JWT decode
    return {
      id: '1',
      email: 'user@example.com',
      name: 'Current User',
      role: 'user',
      createdAt: new Date().toISOString(),
    };
  },

  isAuthenticated(): boolean {
    return !!Cookies.get('auth-token');
  }
};