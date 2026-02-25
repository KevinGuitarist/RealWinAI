import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { getCurrentUser } from "@/lib/auth";
import { useAuth } from "@/components/auth/AuthProvider";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const user = getCurrentUser();
  const { logout } = useAuth();
  const navigate = useNavigate();
  const firstName = user?.first_name || user?.email?.split('@')[0] || 'User';

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background overflow-hidden">
        <AppSidebar />
        
        <main className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <header className="h-16 border-b border-border bg-surface flex items-center px-6 flex-shrink-0">
            <SidebarTrigger className="text-foreground" />
            
            {/* Logo - visible on mobile */}
            <div className="flex-1 flex justify-center lg:hidden">
              <button 
                onClick={() => navigate('/dashboard')}
                className="flex items-center"
              >
                <img 
                  src="/favicon.png" 
                  alt="RealWin.AI" 
                  className="h-8 w-auto cursor-pointer hover:opacity-80 transition-opacity"
                />
              </button>
            </div>
            
            <div className="ml-auto lg:ml-auto">
              <div className="flex items-center gap-4">
                <div className="text-sm text-muted-foreground">
                  Welcome back, <span className="text-foreground font-medium">{firstName}</span>
                </div>
                <Button 
                  size="sm" 
                  onClick={() => {
                    logout();
                    navigate('/login');
                  }}
                  className="text-black hover:opacity-90"
                  style={{ backgroundColor: 'hsl(var(--brand-accent))' }}
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          </header>
          
          {/* Content */}
          <div className="flex-1 p-6 overflow-auto min-w-0">
            {children}
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}