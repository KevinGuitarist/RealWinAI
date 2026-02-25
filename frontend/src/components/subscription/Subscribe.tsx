
import React, { useEffect, useState } from "react";
import { getMySubscription } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { getCurrentUser, getAccessToken, isTokenExpired, clearAuthTokens } from "@/lib/auth";
import { PricingConfig } from "@/hooks/useLocationPricing";
import { config } from "@/lib/config";


type Status = string | null;

interface SubscribeProps {
  onSubscriptionActivated?: () => void;
  isModal?: boolean;
  pricing?: PricingConfig;
}

export default function Subscribe({ onSubscriptionActivated, isModal = false, pricing }: SubscribeProps = {}) {
  const user = getCurrentUser();
  const [email, setEmail] = useState(user?.email || "");
  const [fullName, setFullName] = useState(`${user?.first_name || ""} ${user?.last_name || ""}`.trim() || "");
  const [status, setStatus] = useState<Status>(null);
  const { toast } = useToast();


  const [isActive, setIsActive] = useState<boolean | null>(null);
  const [isCheckingStatus, setIsCheckingStatus] = useState(true);

  // Check subscription status on mount and redirect if active
  useEffect(() => {
    // Skip if we're in modal mode and parent already checked
    if (isModal) {
      setIsCheckingStatus(false);
      return;
    }
    
    (async () => {
      try {
        const sub = await getMySubscription();
        setIsActive(sub.is_active);
        
        // If user is already active
        if (sub.is_active) {
          // For modal usage, close modal and redirect immediately
          if (isModal) {
            onSubscriptionActivated?.(); // Close modal
            window.location.href = '/dashboard';
            return;
          }
          
          // For subscription page, just show active status without redirecting
          setIsActive(true);
          setIsCheckingStatus(false);
        } else {
          setIsCheckingStatus(false); // Only stop loading if user is inactive
        }
      } catch {
        // no sub yet; show subscription form
        setIsActive(false);
        setIsCheckingStatus(false);
      }
    })();
  }, [toast, isModal, onSubscriptionActivated]);

  // Remove auto-initialization since we're using redirect now


  async function redirectToCheckout() {
    try {
      console.log("Starting subscription with:", { email, fullName });
      
      if (!email || !fullName) {
        setStatus("Enter name and email first.");
        toast({
          variant: "destructive",
          title: "Missing Information",
          description: "Please enter your name and email first.",
        });
        return;
      }

      // Check if token is expired before making the request
      if (isTokenExpired()) {
        setStatus("Session expired. Please log in again.");
        toast({
          variant: "destructive",
          title: "Session Expired",
          description: "Your session has expired. Please log in again.",
        });
        clearAuthTokens();
        window.location.href = '/login';
        return;
      }

      // Disable the button to prevent multiple clicks
      const payButton = document.querySelector('[data-payment-button]') as HTMLButtonElement;
      if (payButton) {
        payButton.disabled = true;
        payButton.style.pointerEvents = 'none';
      }

      // Validate name has at least 2 words
      const nameWords = fullName.trim().split(/\s+/).filter(word => word.length > 0);
      if (nameWords.length < 2) {
        setStatus("Full name must contain at least two words (first and last name).");
        toast({
          variant: "destructive",
          title: "Invalid Name",
          description: "Full name must contain at least two words (first and last name).",
        });
        // Re-enable button on validation error
        if (payButton) {
          payButton.disabled = false;
          payButton.style.pointerEvents = 'auto';
        }
        return;
      }

      setStatus(`Creating ${pricing?.trialPriceFormatted || '£1.00'} order...`);
      console.log("Calling Stripe subscription API...");
      
      // Get fresh token
      const token = getAccessToken();
      console.log("Token retrieved:", token ? "Token exists" : "No token found");
      console.log("Token length:", token?.length || 0);
      
      if (!token) {
        setStatus("Authentication required. Please log in again.");
        toast({
          variant: "destructive",
          title: "Authentication Required",
          description: "Please log in again.",
        });
        clearAuthTokens();
        window.location.href = '/login';
        return;
      }

      console.log("Making request to:", `${config.API_BASE_URL}/subscriptions/stripe/start`);
      console.log("Request headers:", {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token.substring(0, 10)}...` // Only log first 10 chars for security
      });

      const res = await fetch(`${config.API_BASE_URL}/subscriptions/stripe/start`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ email, full_name: fullName }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => null);
        throw new Error(err?.detail || err?.message || `HTTP ${res.status}`);
      }

      const response: { checkout_url: string } = await res.json();
      console.log("Stripe API Response:", response);
      
      if (!response || !response.checkout_url) {
        throw new Error("No checkout URL received from Stripe API");
      }
      
      const { checkout_url } = response;
      setStatus("Redirecting to Stripe Checkout...");
      console.log("Redirecting to Stripe checkout URL:", checkout_url);
      
      // Redirect to the Stripe checkout URL provided by the API
      window.location.href = checkout_url;
      
    } catch (e: any) {
      const errorMsg = `Failed to start: ${e?.message || String(e)}`;
      setStatus(errorMsg);
      toast({
        variant: "destructive",
        title: "Setup Error",
        description: e?.message || "Failed to start subscription process.",
      });
      // Re-enable button and restore modal visibility on error
      const payButton = document.querySelector('[data-payment-button]') as HTMLButtonElement;
      const modalElement = document.querySelector('[role="dialog"]') as HTMLElement;
      if (payButton) {
        payButton.disabled = false;
        payButton.style.pointerEvents = 'auto';
      }
      if (modalElement) {
        modalElement.style.display = 'block';
      }
    }
  }

  // Removed pay function since we're redirecting to checkout

  // Poll backend until webhook marks subscription active
  async function pollUntilActive() {
    let tries = 0;
    const maxTries = 12; // ~60s if interval=5s
    const interval = 5000;

    const iv = setInterval(async () => {
      tries++;
      try {
        const sub = await getMySubscription();
        setIsActive(sub.is_active);
        if (sub.is_active) {
          setStatus(`Subscription active! You'll be billed ${pricing?.monthlyPriceFormatted || '£19.99'} monthly.`);
          toast({
            title: "Subscription Active!",
            description: `You'll be billed ${pricing?.monthlyPriceFormatted || '£19.99'} monthly starting in 7 days.`,
          });
          clearInterval(iv);
          // Notify parent component that subscription is now active
          onSubscriptionActivated?.();
          
          // Redirect to dashboard after successful activation
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 1500);
        } else if (tries >= maxTries) {
          setStatus("Payment completed but not active yet. Please refresh later.");
          toast({
            variant: "destructive",
            title: "Verification Timeout",
            description: "Payment completed but not active yet. Please refresh later.",
          });
          clearInterval(iv);
        } else {
          setStatus(`Waiting for webhook... (attempt ${tries}/${maxTries})`);
        }
      } catch {
        if (tries >= maxTries) {
          setStatus("Couldn't verify status yet. Try again soon.");
          toast({
            variant: "destructive",
            title: "Verification Failed",
            description: "Couldn't verify status yet. Try again soon.",
          });
          clearInterval(iv);
        }
      }
    }, interval);
  }

  // Show loading while checking status
  if (isCheckingStatus) {
    const loadingContent = (
      <div className="space-y-4 text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-primary mx-auto"></div>
        <p className="text-muted-foreground">Checking subscription status...</p>
      </div>
    );

    if (isModal) {
      return loadingContent;
    }

    return (
      <Card className="max-w-md mx-auto">
        <CardContent className="p-6">
          {loadingContent}
        </CardContent>
      </Card>
    );
  }

  // If user already has active subscription, show success message instead
  if (isActive === true) {
    const content = (
      <div className="space-y-4 text-center">
        <div className="space-y-2">
          <h2 className="text-xl font-semibold text-brand-accent">Subscription Active!</h2>
          <p className="text-muted-foreground">
            You're all set! Your subscription is active and you'll be billed{" "}
            <span className="font-bold text-brand-primary">{pricing?.monthlyPriceFormatted || '£19.99'}/month</span>.
          </p>
        </div>
        <div className="bg-brand-primary/10 rounded-lg p-4 border border-brand-primary/20">
          <span className="font-bold text-green-600">✓ Premium Access Enabled</span>
        </div>
      </div>
    );

    if (isModal) {
      return content;
    }

    return (
      <Card className="max-w-md mx-auto">
        <CardContent className="p-6">
          {content}
        </CardContent>
      </Card>
    );
  }

  const subscriptionContent = (
    <div className="space-y-4">
      <div className="text-center space-y-2">
        <h2 className="text-xl font-semibold text-brand-accent">Monthly Plan</h2>
        <p className="text-muted-foreground">
          {!pricing ? (
            <span className="animate-pulse">Loading pricing...</span>
          ) : (
            <>
              Pay <span className="font-bold text-brand-primary">{pricing.trialPriceFormatted} now</span>, then{" "}
              <span className="font-bold text-brand-primary">{pricing.monthlyPriceFormatted}/month</span> (auto-billed).
            </>
          )}
        </p>
      </div>

      {/* Show user details */}
      <div className="bg-muted/30 rounded-lg p-4 space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className="text-muted-foreground">Name:</span>
          <span className="font-medium">{fullName}</span>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-muted-foreground">Email:</span>
          <span className="font-medium truncate ml-2">{email}</span>
        </div>
      </div>

      {/* Redirect to checkout */}
      <Button 
        onClick={redirectToCheckout} 
        className="w-full bg-brand-primary hover:bg-brand-primary-hover relative"
        disabled={!email || !fullName || !pricing}
        data-payment-button
        style={{ zIndex: 1 }}
      >
        {!pricing ? (
          <div className="flex items-center gap-2">
            <div className="animate-pulse bg-white/20 rounded h-4 w-20"></div>
          </div>
        ) : (
          `Pay ${pricing.trialPriceFormatted}`
        )}
      </Button>

      {isActive !== null && (
        <div className="text-center text-sm">
          Status:{" "}
          {isActive ? (
            <span className="font-bold text-green-600">Active</span>
          ) : (
            <span className="font-bold text-orange-600">Inactive</span>
          )}
        </div>
      )}

      {status && (
        <div className="text-sm text-muted-foreground text-center bg-surface/50 rounded-lg p-3">
          {status}
        </div>
      )}
    </div>
  );

  if (isModal) {
    return subscriptionContent;
  }

  return (
    <Card className="max-w-md mx-auto">
      <CardContent className="p-6">
        {subscriptionContent}
      </CardContent>
    </Card>
  );
}
