import React, { createContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state on app load. There's no /auth/me endpoint (lean
  // backend, login-only) so this trusts the userData cached alongside the
  // token at login time rather than re-verifying against the server; an
  // expired/invalid token still gets caught by api.js's 401 interceptor on
  // the next real request.
  useEffect(() => {
    const token = localStorage.getItem('token');
    const cachedUser = localStorage.getItem('userData');
    if (token && cachedUser) {
      try {
        setUser(JSON.parse(cachedUser));
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Invalid cached session');
        localStorage.removeItem('token');
        localStorage.removeItem('userData');
      }
    }
    setIsLoading(false);
  }, []);

  const persistSession = (token, userData) => {
    localStorage.setItem('token', token);
    localStorage.setItem('userData', JSON.stringify(userData));
    setUser(userData);
    setIsAuthenticated(true);
  };

  const login = useCallback(async (credentials) => {
    setIsLoading(true);
    try {
      const { token, userData } = await authService.login(credentials);
      persistSession(token, userData);
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Invalid credentials',
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (credentials) => {
    setIsLoading(true);
    try {
      const { token, userData } = await authService.register(credentials);
      // Registration logs the new user straight in, same as login.
      persistSession(token, userData);
      return { success: true };
    } catch (error) {
      console.error('Registration failed:', error);
      return {
        success: false,
        error: error.response?.data?.detail || 'Could not create account',
      };
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('userData');
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};