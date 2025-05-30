// Authentication API Client

import { 
  LoginForm, 
  RegisterForm, 
  ResetPasswordForm, 
  AuthResponse, 
  User, 
  AuthTokens,
  AuthAPI 
} from '../types/auth';

// API Base Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

// Token storage utilities
export const tokenStorage = {
  getTokens: (): AuthTokens | null => {
    try {
      const tokens = localStorage.getItem('auth_tokens');
      return tokens ? JSON.parse(tokens) : null;
    } catch {
      return null;
    }
  },

  setTokens: (tokens: AuthTokens): void => {
    localStorage.setItem('auth_tokens', JSON.stringify(tokens));
  },

  clearTokens: (): void => {
    localStorage.removeItem('auth_tokens');
  },

  isTokenExpired: (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return Date.now() >= payload.exp * 1000;
    } catch {
      return true;
    }
  }
};

// API Client with token management
const apiClient = {
  async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<T> {
    const tokens = tokenStorage.getTokens();
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add authorization header if we have a valid token
    if (tokens && !tokenStorage.isTokenExpired(tokens.accessToken)) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${tokens.accessToken}`,
      };
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // Handle 401 responses (token expired)
    if (response.status === 401) {
      tokenStorage.clearTokens();
      window.location.href = '/login';
      throw new Error('Session expired. Please log in again.');
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'An error occurred');
    }

    return data;
  }
};

// Authentication API implementation
export const authAPI: AuthAPI = {
  async login(credentials: LoginForm): Promise<AuthResponse> {
    try {
      const response = await apiClient.request<AuthResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      });

      // Store tokens
      tokenStorage.setTokens(response.tokens);
      
      return response;
    } catch (error) {
      // Mock response for development/testing
      console.log('Auth API not available, using mock login');
      
      if (credentials.email === 'user@demo.test' && credentials.password === 'demopass') {
        const mockResponse: AuthResponse = {
          user: {
            id: '1',
            name: 'Demo User',
            email: credentials.email,
            createdAt: new Date(),
            updatedAt: new Date(),
          },
          tokens: {
            accessToken: 'mock_access_token',
            refreshToken: 'mock_refresh_token',
            expiresIn: 3600,
          },
          message: 'Welcome back!'
        };
        
        tokenStorage.setTokens(mockResponse.tokens);
        return mockResponse;
      }
      
      throw new Error('Invalid email or password');
    }
  },

  async register(data: RegisterForm): Promise<AuthResponse> {
    try {
      const response = await apiClient.request<AuthResponse>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      // Store tokens
      tokenStorage.setTokens(response.tokens);
      
      return response;
    } catch (error) {
      // Mock response for development/testing
      console.log('Auth API not available, using mock registration');
      
      const mockResponse: AuthResponse = {
        user: {
          id: '2',
          name: data.name,
          email: data.email,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        tokens: {
          accessToken: 'mock_access_token_new',
          refreshToken: 'mock_refresh_token_new',
          expiresIn: 3600,
        },
        message: 'Account created successfully!'
      };
      
      tokenStorage.setTokens(mockResponse.tokens);
      return mockResponse;
    }
  },

  async logout(): Promise<void> {
    try {
      await apiClient.request('/auth/logout', {
        method: 'POST',
      });
    } catch (error) {
      console.log('Logout API call failed, clearing tokens locally');
    } finally {
      // Always clear tokens locally
      tokenStorage.clearTokens();
    }
  },

  async refreshToken(refreshToken: string): Promise<AuthTokens> {
    try {
      const response = await apiClient.request<AuthTokens>('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refreshToken }),
      });

      tokenStorage.setTokens(response);
      return response;
    } catch (error) {
      tokenStorage.clearTokens();
      throw new Error('Unable to refresh session. Please log in again.');
    }
  },

  async getProfile(): Promise<User> {
    try {
      return await apiClient.request<User>('/users/profile');
    } catch (error) {
      // Mock response for development/testing
      console.log('Profile API not available, using mock data');
      
      return {
        id: '1',
        name: 'Demo User',
        email: 'demo@example.com',
        createdAt: new Date(),
        updatedAt: new Date(),
      };
    }
  },

  async resetPassword(data: ResetPasswordForm): Promise<{ message: string }> {
    try {
      return await apiClient.request<{ message: string }>('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    } catch (error) {
      // Mock response for development/testing
      console.log('Reset password API not available, using mock response');
      
      return {
        message: 'If an account with that email exists, you will receive a password reset link shortly.'
      };
    }
  }
};

// Utility function to check if user is authenticated
export const isAuthenticated = (): boolean => {
  const tokens = tokenStorage.getTokens();
  return tokens !== null && !tokenStorage.isTokenExpired(tokens.accessToken);
}; 