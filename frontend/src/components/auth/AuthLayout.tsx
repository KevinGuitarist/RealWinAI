import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { isAuthenticated } from "@/lib/auth";
import { useAuth } from "./AuthProvider";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
}

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  const navigate = useNavigate();
  const { logout, isLoggedIn } = useAuth();

  useEffect(() => {
    // Redirect authenticated users to dashboard unless they're signing up
    if (isAuthenticated() && isLoggedIn && title !== "Create your account") {
      navigate('/dashboard', { replace: true });
    }
  }, [navigate, isLoggedIn, title]);

  const showLogoutButton = isLoggedIn && title === "Create your account";

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="w-full max-w-md space-y-6">
        {/* Logout button for signup flow */}
        {showLogoutButton && (
          <div className="flex justify-end">
            <Button 
              onClick={logout}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        )}

        <div className="text-center space-y-4">
          <img 
            src="https://realwin.ai/static/images/logo-transparent.png" 
            alt="RealWin.AI" 
            className="h-12 mx-auto"
          />
          <div>
            <h1 className="text-2xl font-bold text-foreground">{title}</h1>
            {subtitle && (
              <p className="text-muted-foreground mt-2">{subtitle}</p>
            )}
          </div>
        </div>
        
        <div className="bg-card border border-border rounded-lg p-6 shadow-card">
          {children}
        </div>
      </div>
    </div>
  );
}