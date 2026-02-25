import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { AuthProvider } from "@/components/auth/AuthProvider";
import { SubscriptionGate } from "@/components/subscription/SubscriptionGate";
import FloatingChatbot from "@/components/chatbot/FloatingChatbot";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Dashboard from "./pages/Dashboard";
import Billing from "./pages/Billing";
import Settings from "./pages/Settings";
import Chatbot from "./pages/Chatbot";
import FootballPredictions from "./pages/FootballPredictions";
import CricketPredictions from "./pages/CricketPredictions";
import CricketDetails from "./pages/CricketDetails";
import MatchAnalysis from "./pages/MatchAnalysis";
import FootballAnalysis from "./pages/FootballAnalysis";
import Subscription from "./pages/Subscription";
import UserSubscriptions from "./pages/UserSubscriptions";
import AdminPredictions from "./pages/AdminPredictions";
import PaymentSuccess from "./pages/PaymentSuccess";
import NotFound from "./pages/NotFound";
import TrackRecord from "./pages/TrackRecord";
import Analytics from "./pages/Analytics";
import StrategySetup from "./pages/StrategySetup";

import { useAuth } from "@/components/auth/AuthProvider";
import { useLocation } from "react-router-dom";
import StripePayment from "./pages/StripePayment";
import AdminJobs from "./pages/AdminJobs";


const queryClient = new QueryClient();

// Component to conditionally render FloatingChatbot on protected pages
const ChatbotWrapper = () => {
  const { isLoggedIn } = useAuth();
  const location = useLocation();

  // Only show chatbot on authenticated routes, but exclude billing and settings
  if (!isLoggedIn) return null;

  // Hide chatbot on billing and settings pages
  if (location.pathname === "/billing" || location.pathname === "/settings") {
    return null;
  }

  return <FloatingChatbot />;
};


const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AuthProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Login />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            {/* <Route path="/stripe-payment" element={<ProtectedRoute><StripePayment /></ProtectedRoute>} /> */}

            
            {/* Protected routes with subscription gate */}
            <Route path="/dashboard" element={<ProtectedRoute><SubscriptionGate><Dashboard /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/billing" element={<ProtectedRoute><SubscriptionGate><Billing /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><SubscriptionGate><Settings /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/chatbot" element={<ProtectedRoute><SubscriptionGate><Chatbot /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/football-predictions" element={<ProtectedRoute><SubscriptionGate><FootballPredictions /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/cricket-predictions" element={<ProtectedRoute><SubscriptionGate><CricketPredictions /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/cricket-details/:matchId" element={<ProtectedRoute><SubscriptionGate><CricketDetails /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/subscription" element={<ProtectedRoute><Subscription /></ProtectedRoute>} />
            <Route path="/payment-success" element={<ProtectedRoute><PaymentSuccess /></ProtectedRoute>} />
            <Route path="/match-analysis/:matchId" element={<ProtectedRoute><SubscriptionGate><MatchAnalysis /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/football-analysis/:matchId" element={<ProtectedRoute><SubscriptionGate><FootballAnalysis /></SubscriptionGate></ProtectedRoute>} />
            
            {/* Enhanced MAX Features */}
            <Route path="/track-record" element={<ProtectedRoute><SubscriptionGate><TrackRecord /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/analytics" element={<ProtectedRoute><SubscriptionGate><Analytics /></SubscriptionGate></ProtectedRoute>} />
            <Route path="/strategy-setup" element={<ProtectedRoute><SubscriptionGate><StrategySetup /></SubscriptionGate></ProtectedRoute>} />
            
            {/* Admin routes */}
            <Route path="/admin/predictions" element={<ProtectedRoute><AdminPredictions /></ProtectedRoute>} />
            <Route path="/admin/subscriptions" element={<ProtectedRoute><UserSubscriptions /></ProtectedRoute>} />
            <Route path="/admin/jobs" element={<ProtectedRoute><AdminJobs /></ProtectedRoute>} />
            
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        {/* Global Floating Chatbot - only shows on authenticated pages */}
          <ChatbotWrapper />
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
