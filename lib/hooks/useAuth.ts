// Authentication Hook

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import { 
  User, 
  AuthError, 
  LoginForm, 
  RegisterForm, 
  UseAuthReturn 
} from '../types/auth';
import { authAPI, tokenStorage, isAuthenticated } from '../api/auth';

export const useAuth = (): UseAuthReturn => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<AuthError | null>(null);
  const router = useRouter();

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (isAuthenticated()) {
          const profile = await authAPI.getProfile();
          setUser(profile);
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        tokenStorage.clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Login function
  const login = useCallback(async (credentials: LoginForm) => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await authAPI.login(credentials);
      setUser(response.user);

      // Redirect to intended page or dashboard
      const returnUrl = router.query.returnUrl as string || '/';
      router.push(returnUrl);
    } catch (error) {
      setError({
        message: error instanceof Error ? error.message : 'Login failed',
        field: 'general'
      });
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  // Register function
  const register = useCallback(async (data: RegisterForm) => {
    try {
      setIsLoading(true);
      setError(null);

      // Validate passwords match
      if (data.password !== data.confirmPassword) {
        throw new Error('Passwords do not match');
      }

      const response = await authAPI.register(data);
      setUser(response.user);

      // Redirect to dashboard after successful registration
      router.push('/');
    } catch (error) {
      setError({
        message: error instanceof Error ? error.message : 'Registration failed',
        field: 'general'
      });
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  // Logout function
  const logout = useCallback(async () => {
    try {
      setIsLoading(true);
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsLoading(false);
      router.push('/login');
    }
  }, [router]);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError,
  };
}; 