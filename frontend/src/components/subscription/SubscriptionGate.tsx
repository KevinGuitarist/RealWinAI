import React, { useEffect, useState } from "react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import Subscribe from "./Subscribe";
import { Loader2 } from "lucide-react";
import { useLocationPricing } from "@/hooks/useLocationPricing";
import { useAuth } from "@/components/auth/AuthProvider";
import { getAccessToken } from "@/lib/auth";
import { config } from "@/lib/config";

interface SubscriptionGateProps {
  children: React.ReactNode;
}

export function SubscriptionGate({ children }: SubscriptionGateProps) {
  const [isLoading, setIsLoading] = useState(true);
  const [isCheckingPaymentStatus, setIsCheckingPaymentStatus] = useState(false);
  const [hasActiveSubscription, setHasActiveSubscription] = useState<boolean>(false);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState<boolean>(false);
  const { pricing, loading: pricingLoading, error: pricingError } = useLocationPricing();
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    // Only check subscription after user is authenticated
    if (isLoggedIn) {
      // Don't show subscription popup immediately after signup
      const justSignedUp = sessionStorage.getItem('just_signed_up');
      if (justSignedUp === '1') {
        sessionStorage.removeItem('just_signed_up');
        setIsLoading(false);
        setHasActiveSubscription(false);
        setShowSubscriptionModal(false); // Give user a moment before showing modal
        
        // Show modal after a short delay to let user see the dashboard first
        setTimeout(() => {
          checkSubscriptionStatus();
        }, 2000);
        return;
      }
      
      checkSubscriptionStatus();
    }
    
    // Add listener for when coming back from payment
    const handleVisibilityChange = () => {
      if (!document.hidden && sessionStorage.getItem('just_paid') === '1') {
        setIsCheckingPaymentStatus(true);
        checkSubscriptionStatus();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isLoggedIn]);

  const checkSubscriptionStatus = async () => {
    if (!isLoggedIn) {
      setIsLoading(false);
      return;
    }

    // TEMPORARY: Grant free access to all logged-in users
    setHasActiveSubscription(true);
    setShowSubscriptionModal(false);
    setIsLoading(false);
    setIsCheckingPaymentStatus(false);
    return;

    /* Original subscription check - disabled for free access
    try {
      const token = getAccessToken();
      if (!token) {
        setHasActiveSubscription(false);
        setShowSubscriptionModal(true);
        return;
      }

      const response = await fetch(`${config.API_BASE_URL}/subscriptions/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const subscription = await response.json();
        console.log('Subscription status:', subscription);
        const active = !!subscription.is_active;
        setHasActiveSubscription(active);
        setShowSubscriptionModal(!active);
      } else if (response.status === 401 || response.status === 403) {
        // Token expired, let AuthProvider handle it
        return;
      } else {
        setHasActiveSubscription(false);
        setShowSubscriptionModal(true);
      }
    } catch (error) {
      console.error('Subscription check error:', error);
      setHasActiveSubscription(false);
      setShowSubscriptionModal(true);
    } finally {
      setIsLoading(false);
      setIsCheckingPaymentStatus(false);
    }
    */
  };

  // Helper to fetch current subscription active state
  const fetchIsActive = async (): Promise<boolean> => {
    const token = getAccessToken();
    if (!token) return false;
    const response = await fetch(`${config.API_BASE_URL}/subscriptions/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    if (response.ok) {
      const subscription = await response.json();
      return !!subscription.is_active;
    }
    throw new Error('Failed to fetch subscription');
  };

  // Poll for activation when returning from payment
  const pollUntilActive = () => {
    let tries = 0;
    const maxTries = 12; // ~60s
    const intervalMs = 5000;
    setIsCheckingPaymentStatus(true);
    const iv = setInterval(async () => {
      tries++;
      try {
        const active = await fetchIsActive();
        if (active) {
          setHasActiveSubscription(true);
          setShowSubscriptionModal(false);
          setIsCheckingPaymentStatus(false);
          sessionStorage.removeItem('just_paid');
          clearInterval(iv);
        } else if (tries >= maxTries) {
          setIsCheckingPaymentStatus(false);
          setShowSubscriptionModal(true);
          sessionStorage.removeItem('just_paid');
          clearInterval(iv);
        }
      } catch (e) {
        if (tries >= maxTries) {
          setIsCheckingPaymentStatus(false);
          setShowSubscriptionModal(true);
          sessionStorage.removeItem('just_paid');
          clearInterval(iv);
        }
      }
    }, intervalMs);
  };

  // If user just returned from successful payment or just logged in with pending payment, verify until active
  useEffect(() => {
    if (!isLoggedIn) return;
    if (sessionStorage.getItem('just_paid') === '1') {
      // Clear any existing check and start fresh polling
      pollUntilActive();
    }
  }, [isLoggedIn]);

  const handleSubscriptionActivated = () => {
    // When subscription becomes active, refresh the status
    setHasActiveSubscription(true);
    setShowSubscriptionModal(false);
    // Clear any cached data to force fresh check
    sessionStorage.removeItem('subscription_data');
  };

  // Show loading spinner while checking subscription
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 animate-spin text-brand-primary mx-auto" />
          <p className="text-muted-foreground mt-4">Loading subscription status...</p>
        </div>
      </div>
    );
  }

  // Show payment status check loader when returning from payment
  if (isCheckingPaymentStatus) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-16 h-16 animate-spin text-brand-primary mx-auto" />
          <div>
            <h3 className="text-lg font-semibold text-foreground">Verifying Payment Status</h3>
            <p className="text-muted-foreground">Please wait while we confirm your subscription...</p>
          </div>
        </div>
      </div>
    );
  }

  // If user has active subscription, render the children (main app)
  if (hasActiveSubscription) {
    return <>{children}</>;
  }

  // If no active subscription, show the subscription modal
  return (
    <>
      {/* Render a heavily blurred background of the app */}
      <div className="min-h-screen bg-background opacity-10 pointer-events-none blur-sm">
        {children}
      </div>
      
      {/* Subscription Modal - Cannot be closed by user */}
      <Dialog open={showSubscriptionModal} onOpenChange={() => {}}>
        <DialogContent className="sm:max-w-lg bg-card/95 backdrop-blur-sm border border-brand-primary/20 shadow-2xl" hideCloseButton>
          <div className="space-y-6 p-2">
            <div className="text-center space-y-3">
              <div className="w-16 h-16 mx-auto bg-gradient-to-br from-brand-primary to-brand-accent rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-brand-accent">Premium Access Required</h2>
                <p className="text-muted-foreground mt-2">
                  Subscribe to unlock all features and get access to advanced sports predictions
                </p>
              </div>
            </div>
            <div className="bg-gradient-to-r from-brand-primary/5 to-brand-accent/5 rounded-lg p-4">
              <Subscribe onSubscriptionActivated={handleSubscriptionActivated} isModal={true} pricing={pricing} />
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}