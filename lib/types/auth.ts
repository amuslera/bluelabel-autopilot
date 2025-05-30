// Authentication Type Definitions

export interface LoginForm {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterForm {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
  agreeToTerms: boolean;
}

export interface ResetPasswordForm {
  email: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface AuthResponse {
  user: User;
  tokens: AuthTokens;
  message?: string;
}

export interface AuthError {
  message: string;
  field?: string;
  code?: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: AuthError | null;
}

// Component Props
export interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  showLogo?: boolean;
}

export interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectTo?: string;
}

export interface UserMenuProps {
  user: User;
  onLogout: () => void;
}

// API Interfaces
export interface AuthAPI {
  login: (credentials: LoginForm) => Promise<AuthResponse>;
  register: (data: RegisterForm) => Promise<AuthResponse>;
  logout: () => Promise<void>;
  refreshToken: (refreshToken: string) => Promise<AuthTokens>;
  getProfile: () => Promise<User>;
  resetPassword: (data: ResetPasswordForm) => Promise<{ message: string }>;
}

// Hook Return Types
export interface UseAuthReturn {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: AuthError | null;
  login: (credentials: LoginForm) => Promise<void>;
  register: (data: RegisterForm) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

// Token Storage
export interface TokenStorage {
  getTokens: () => AuthTokens | null;
  setTokens: (tokens: AuthTokens) => void;
  clearTokens: () => void;
  isTokenExpired: (token: string) => boolean;
} 