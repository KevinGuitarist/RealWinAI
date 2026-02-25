import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { isAuthenticated, clearAuthTokens, getAccessToken, logout as authLogout } from '@/lib/auth';

interface AuthContextType {
  isLoggedIn: boolean;
  token: string | null;
  logout: () => void;
  checkAuth: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  const checkAuth = () => {
    const authStatus = isAuthenticated();
    const currentToken = getAccessToken();
    setIsLoggedIn(authStatus);
    setToken(currentToken);
    
    if (!authStatus && currentToken) {
      // Token exists but expired
      clearAuthTokens();
      setToken(null);
      window.location.href = '/login';
    }
  };

  const logout = () => {
    authLogout();
  };

  useEffect(() => {
    checkAuth();
    
    // Check auth status every minute
    const interval = setInterval(checkAuth, 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  // Listen for storage changes (logout from another tab)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token' && !e.newValue) {
        // Token was removed, update auth state
        setIsLoggedIn(false);
        setToken(null);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const value = {
    isLoggedIn,
    token,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};