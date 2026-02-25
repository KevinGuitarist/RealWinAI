import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Zap, MapPin } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Subscribe from "@/components/subscription/Subscribe";
import SubscriptionStatus from "@/components/subscription/SubscriptionStatus";
import { useState } from "react";
import { useLocationPricing } from "@/hooks/useLocationPricing";

const Subscription = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<"subscribe" | "status">("subscribe");
  const { pricing, loading: pricingLoading, error: pricingError } = useLocationPricing();

  const features = [
    "Access to all sports predictions (Football & Cricket)",
    "Advanced AI-powered match analysis with 90%+ accuracy",
    "Real-time odds comparison & value betting insights",
    "Detailed team statistics and head-to-head records",
    "Live match tracking and updates",
    "Priority customer support",
    "Mobile-optimized responsive interface"
  ];

  const handleSubscribe = () => {
    // TODO: Implement Stripe checkout
    console.log("Subscribe clicked - Stripe integration needed");
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Back Button */}
          <Button 
            variant="outline" 
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 border-brand-primary text-brand-accent hover:bg-brand-primary hover:text-background"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Sports Selection
          </Button>

          {/* Tab Navigation */}
          <div className="flex space-x-1 bg-surface rounded-lg p-1">
            <Button
              variant={activeTab === "subscribe" ? "default" : "ghost"}
              onClick={() => setActiveTab("subscribe")}
              className="flex-1"
            >
              Subscribe
            </Button>
            <Button
              variant={activeTab === "status" ? "default" : "ghost"}
              onClick={() => setActiveTab("status")}
              className="flex-1"
            >
              Manage Subscription
            </Button>
          </div>

          {/* Tab Content */}
          {activeTab === "subscribe" ? (
            <>
              {/* Subscription Info Card */}
              <Card className="relative overflow-hidden bg-gradient-to-br from-card via-surface to-card border-2 border-brand-primary shadow-brand">
                {/* Background Pattern */}
                <div className="absolute inset-0 opacity-5">
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,hsl(82_100%_50%),transparent_50%)]"></div>
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,hsl(82_100%_50%),transparent_50%)]"></div>
                </div>
                
                <CardContent className="relative p-8 space-y-8">
                  {/* Premium Access Badge */}
                  <div className="text-center">
                    <div className="inline-flex items-center gap-2 bg-gradient-to-r from-brand-primary to-brand-primary-hover text-background px-6 py-3 rounded-full text-sm font-bold shadow-brand animate-pulse">
                      <Zap className="w-4 h-4" />
                      PREMIUM ACCESS
                      <Zap className="w-4 h-4" />
                    </div>
                  </div>

                  {/* Title and Description */}
                  <div className="text-center space-y-4">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-accent to-foreground bg-clip-text text-transparent">
                      Sports Prediction Pro
                    </h1>
                    <p className="text-lg text-muted-foreground max-w-md mx-auto">
                      Unlock professional-grade sports predictions with AI-powered analysis
                    </p>
                  </div>

                  {/* Price Section with Enhanced Design */}
                  <div className="text-center space-y-4">
                    {/* Location indicator */}
                    {!pricingLoading && (
                      <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                        <MapPin className="w-4 h-4" />
                        <span>Pricing for {pricing.country}</span>
                      </div>
                    )}
                    
                    {/* Trial Price */}
                    <div className="relative bg-gradient-to-r from-brand-primary/20 to-brand-primary/10 rounded-2xl p-6 border border-brand-primary/30 shadow-lg">
                      <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                        <span className="bg-brand-primary text-background px-4 py-1 rounded-full text-xs font-bold">
                          TRIAL OFFER
                        </span>
                      </div>
                      <div className="text-3xl font-bold text-brand-accent mb-2">
                        {pricingLoading ? (
                          <div className="animate-pulse bg-muted rounded h-12 w-32 mx-auto"></div>
                        ) : (
                          <span className="text-5xl">{pricing.trialPriceFormatted}</span>
                        )}
                      </div>
                      <p className="text-brand-accent font-medium">for first 7 days</p>
                    </div>
                    
                    {/* Regular Price */}
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground mb-2">then</p>
                      <div className="text-4xl font-bold text-foreground">
                        {pricingLoading ? (
                          <div className="animate-pulse bg-muted rounded h-16 w-48 mx-auto"></div>
                        ) : (
                          <>
                            <span className="text-5xl bg-gradient-to-r from-brand-accent to-foreground bg-clip-text text-transparent">
                              {pricing.monthlyPriceFormatted}
                            </span>
                            <span className="text-xl text-muted-foreground">/month</span>
                          </>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">Cancel anytime</p>
                    </div>
                    
                    {/* Pricing error fallback */}
                    {pricingError && (
                      <div className="text-xs text-muted-foreground bg-muted/30 rounded-lg p-2">
                        {pricingError}
                      </div>
                    )}
                  </div>

                  {/* Features List with Enhanced Design */}
                  <div className="bg-gradient-to-br from-surface/80 to-muted/40 rounded-2xl p-6 border border-border/50 shadow-inner">
                    <h3 className="text-lg font-semibold text-foreground mb-4 text-center">What You Get:</h3>
                    <div className="space-y-4">
                      {features.map((feature, index) => (
                        <div key={index} className="flex items-start gap-3 group">
                          <div className="w-6 h-6 bg-brand-primary/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 group-hover:bg-brand-primary/30 transition-colors">
                            <Zap className="w-3 h-3 text-brand-accent" />
                          </div>
                          <span className="text-foreground leading-relaxed">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Security Note with Enhanced Design */}
                  <div className="bg-gradient-to-r from-surface/60 to-muted/30 rounded-xl p-4 border border-border/40">
                    <div className="flex items-center gap-3 text-sm">
                      <div className="w-8 h-8 bg-brand-primary/20 rounded-full flex items-center justify-center flex-shrink-0">
                        <div className="w-3 h-3 bg-brand-primary rounded-full animate-pulse"></div>
                      </div>
                      <span className="text-muted-foreground">
                        <strong className="text-brand-accent">Bank-level security</strong> powered by Revolut. 
                        Your payment information is encrypted and protected.
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              {/* Payment Component */}
              <Subscribe pricing={pricing} />
            </>
          ) : (
            <SubscriptionStatus />
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Subscription;