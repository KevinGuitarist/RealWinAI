import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated, clearAuthTokens, isTokenExpired } from '@/lib/auth';
import { useAuth } from './AuthProvider';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const navigate = useNavigate();
  const { isLoggedIn, checkAuth } = useAuth();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const validateAccess = () => {
      checkAuth();
      
      if (!isAuthenticated() || isTokenExpired()) {
        clearAuthTokens();
        navigate('/login', { replace: true });
      } else {
        setIsChecking(false);
      }
    };

    validateAccess();
  }, [navigate, checkAuth]);

  // Show loading while checking authentication
  if (isChecking || !isLoggedIn) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Verifying authentication...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};