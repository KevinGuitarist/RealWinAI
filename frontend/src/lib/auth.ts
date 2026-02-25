interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    first_name: string | null;
    last_name: string | null;
    role?: string;
  };
}

interface SignupData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  source?: string;
}

interface LoginData {
  email: string;
  password: string;
}

import { config } from './config';

export const signupUser = async (data: SignupData): Promise<AuthResponse> => {
  const response = await fetch(`${config.API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Signup failed');
  }

  return response.json();
};

export const loginUser = async (data: LoginData): Promise<AuthResponse> => {
  const response = await fetch(`${config.API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: data.email,
      password: data.password
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Login failed');
  }

  return response.json();
};

export const saveAuthTokens = (authResponse: AuthResponse) => {
  localStorage.setItem('access_token', authResponse.access_token);
  localStorage.setItem('refresh_token', authResponse.refresh_token);

  // Ensure role has a default value
  const userWithRole = {
    ...authResponse.user,
    role: authResponse.user.role || 'User'
  };

  localStorage.setItem('user', JSON.stringify(userWithRole));
  localStorage.setItem('token_expires_at', (Date.now() + config.TOKEN_EXPIRY_HOURS * 60 * 60 * 1000).toString());
};

export const getAccessToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const isTokenExpired = (): boolean => {
  const expiresAt = localStorage.getItem('token_expires_at');
  if (!expiresAt) return true;
  return Date.now() > parseInt(expiresAt);
};

export const clearAuthTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  localStorage.removeItem('token_expires_at');
};

export const forgotPassword = async (email: string): Promise<void> => {
  const response = await fetch(`${config.API_BASE_URL}/auth/forgot-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'accept': 'application/json',
    },
    body: JSON.stringify({ email }),
  });

  // Always return success regardless of actual response
  // This is intentional for security reasons
  return;
};

export const logout = () => {
  // Clear all localStorage data immediately
  clearAuthTokens();

  // Clear all cookies
  document.cookie.split(";").forEach((c) => {
    document.cookie = c
      .replace(/^ +/, "")
      .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
  });

  // Clear session storage as well
  sessionStorage.clear();

  // Redirect to login page immediately
  window.location.replace('/login');
};

export const isAuthenticated = (): boolean => {
  const token = getAccessToken();
  return token !== null && !isTokenExpired();
};

export const resetPassword = async (token: string, newPassword: string): Promise<void> => {
  const response = await fetch(`${config.API_BASE_URL}/auth/reset-password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'accept': 'application/json',
    },
    body: JSON.stringify({
      token,
      new_password: newPassword
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Password reset failed');
  }
};

export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  if (userStr) {
    try {
      const user = JSON.parse(userStr);
      // Ensure role has a default value if missing
      return {
        ...user,
        role: user.role || 'User'
      };
    } catch (error) {
      return null;
    }
  }
  return null;
};

export const getCurrentUserRole = (): string => {
  const user = getCurrentUser();
  return user?.role || 'User';
};