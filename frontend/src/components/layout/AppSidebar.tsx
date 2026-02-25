import { 
  LayoutDashboard, 
  CreditCard, 
  Settings, 
  MessageSquare, 
  LogOut, 
  Star, 
  Users, 
  Lightbulb, 
  Briefcase,
  Award,
  BarChart3,
  Target
} from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import { getCurrentUserRole } from "@/lib/auth";
import { useAuth } from "@/components/auth/AuthProvider";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";

const navigationItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Track Record", url: "/track-record", icon: Award },
  { title: "Analytics", url: "/analytics", icon: BarChart3 },
  { title: "My Strategy", url: "/strategy-setup", icon: Target },
  { title: "Subscription", url: "/subscription", icon: Star },
  { title: "Settings", url: "/settings", icon: Settings },
  { title: "AI Expert", url: "/chatbot", icon: MessageSquare },
];

const adminNavigationItems = [
  { title: "Predictions", url: "/admin/predictions", icon: Lightbulb },
  { title: "User Subscriptions", url: "/admin/subscriptions", icon: Users },
  { title: "Jobs", url: "/admin/jobs", icon: Briefcase },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const location = useLocation();
  const currentPath = location.pathname;
  const isCollapsed = state === "collapsed";
  const userRole = getCurrentUserRole();
  const isAdmin = userRole === "Admin";
  const { logout } = useAuth();

  const isActive = (path: string) => currentPath === path;

  const getNavCls = ({ isActive }: { isActive: boolean }) =>
    isActive 
      ? "bg-brand-primary text-white font-medium shadow-brand" 
      : "hover:bg-surface-hover text-muted-foreground hover:text-foreground";

  const handleLogout = () => {
    logout();
  };

  return (
    <Sidebar className="border-r border-sidebar-border">
      <SidebarContent className="bg-sidebar">
        {/* Logo section */}
        <div className="p-4 border-b border-sidebar-border">
          {!isCollapsed ? (
            <img 
              src="https://realwin.ai/static/images/logo-transparent.png" 
              alt="RealWin.AI" 
              className="h-8"
            />
          ) : (
            <div className="w-6 h-6 bg-brand-primary rounded flex items-center justify-center mx-auto">
              <span className="text-white text-xs font-bold">R</span>
            </div>
          )}
        </div>

        <SidebarGroup>
          <SidebarGroupLabel className="text-muted-foreground">
            {!isCollapsed && "Navigation"}
          </SidebarGroupLabel>

          <SidebarGroupContent>
            <SidebarMenu>
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <NavLink 
                      to={item.url} 
                      end 
                      className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${getNavCls({ isActive })}`}
                    >
                      <item.icon className="h-5 w-5 flex-shrink-0" />
                      {!isCollapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Admin Only Section */}
        {isAdmin && (
          <SidebarGroup>
            <SidebarGroupLabel className="text-muted-foreground">
              {!isCollapsed && "Admin Only"}
            </SidebarGroupLabel>

            <SidebarGroupContent>
              <SidebarMenu>
                {adminNavigationItems.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild>
                      <NavLink 
                        to={item.url} 
                        end 
                        className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${getNavCls({ isActive })}`}
                      >
                        <item.icon className="h-5 w-5 flex-shrink-0" />
                        {!isCollapsed && <span>{item.title}</span>}
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        )}

        {/* Logout button at bottom */}
        <div className="mt-auto p-4 border-t border-sidebar-border">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg transition-all w-full text-left hover:bg-surface-hover text-muted-foreground hover:text-foreground"
          >
            <LogOut className="h-5 w-5 flex-shrink-0" />
            {!isCollapsed && <span>Logout</span>}
          </button>
        </div>
      </SidebarContent>
    </Sidebar>
  );
}