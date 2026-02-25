import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useToast } from "@/hooks/use-toast";
import { setSpendingLimits, getSpendingLimits, requestSelfExclusion } from "@/lib/api";
import { getCurrentUser } from "@/lib/auth";
import { User, Bell, Shield, Globe, AlertTriangle } from "lucide-react";

const Settings = () => {
  const { toast } = useToast();
  const user = getCurrentUser();

  const [limits, setLimits] = useState({
    daily_limit: 0,
    weekly_limit: 0,
    monthly_limit: 0,
  });

  // Fetch existing limits
  useQuery({
    queryKey: ['spendingLimits', user?.id],
    queryFn: () => getSpendingLimits(user?.id || 0),
    enabled: !!user?.id,
    onSuccess: (data) => {
      if (data?.data) {
        setLimits(data.data);
      }
    }
  });

  const updateLimitsMutation = useMutation({
    mutationFn: () => setSpendingLimits(user?.id || 0, limits),
    onSuccess: () => {
      toast({
        title: "Limits Updated",
        description: "Your spending limits have been saved successfully.",
      });
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to update spending limits.",
        variant: "destructive",
      });
    }
  });

  const handleSetLimits = () => {
    updateLimitsMutation.mutate();
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-3 sm:p-6">
        <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8">
          <div className="text-center sm:text-left">
            <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Settings</h1>
            <p className="text-sm sm:text-base text-muted-foreground mt-2">Manage your account preferences and notifications</p>
          </div>
          
          <div className="grid gap-6 max-w-4xl mx-auto">
            {/* Profile Settings */}
            <Card className="bg-card border-card-border shadow-card">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
                  <div className="w-8 h-8 bg-brand-primary/20 rounded-lg flex items-center justify-center">
                    <User className="w-4 h-4 text-brand-accent" />
                  </div>
                  Profile Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-foreground text-sm font-medium">Full Name</Label>
                    <Input 
                      id="name" 
                      placeholder="Enter your full name" 
                      className="bg-surface border-border focus:border-brand-accent"
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-foreground text-sm font-medium">Email Address</Label>
                    <Input 
                      id="email" 
                      type="email" 
                      placeholder="Enter your email" 
                      className="bg-surface border-border focus:border-brand-accent"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-foreground text-sm font-medium">Phone Number</Label>
                  <Input 
                    id="phone" 
                    type="tel" 
                    placeholder="Enter your phone number" 
                    className="bg-surface border-border focus:border-brand-accent"
                  />
                </div>
                
                <Button className="bg-brand-primary hover:bg-brand-primary-hover text-background hover:text-background w-full sm:w-auto">
                  Save Changes
                </Button>
              </CardContent>
            </Card>

            {/* Notification Settings */}
            <Card className="bg-card border-card-border shadow-card">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
                  <div className="w-8 h-8 bg-brand-primary/20 rounded-lg flex items-center justify-center">
                    <Bell className="w-4 h-4 text-brand-accent" />
                  </div>
                  Notification Settings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Match Predictions</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">Get notified about new match predictions and updates</p>
                  </div>
                  <Switch />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Email Notifications</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">Receive important updates via email</p>
                  </div>
                  <Switch />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Push Notifications</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">Get instant alerts on your device</p>
                  </div>
                  <Switch />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Weekly Reports</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">Receive weekly performance summaries</p>
                  </div>
                  <Switch />
                </div>
              </CardContent>
            </Card>

            {/* Privacy & Security */}
            <Card className="bg-card border-card-border shadow-card">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
                  <div className="w-8 h-8 bg-brand-primary/20 rounded-lg flex items-center justify-center">
                    <Shield className="w-4 h-4 text-brand-accent" />
                  </div>
                  Privacy & Security
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Two-Factor Authentication</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">Add an extra layer of security to your account</p>
                  </div>
                  <Switch />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Data Analytics</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">Allow us to collect usage data to improve our service</p>
                  </div>
                  <Switch />
                </div>
              </CardContent>
            </Card>

            {/* Responsible Gambling */}
            <Card className="bg-card border-card-border shadow-card border-yellow-500/20">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
                  <div className="w-8 h-8 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                    <AlertTriangle className="w-4 h-4 text-yellow-500" />
                  </div>
                  Responsible Gambling
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-2">
                  Set limits to help you stay in control of your betting
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Spending Limits */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-foreground">Spending Limits</h3>
                  
                  <div className="grid sm:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="dailyLimit" className="text-foreground text-sm font-medium">
                        Daily Limit (£)
                      </Label>
                      <Input 
                        id="dailyLimit" 
                        type="number"
                        min="0"
                        step="10"
                        placeholder="0 = No limit"
                        value={limits.daily_limit || ''}
                        onChange={(e) => setLimits({ ...limits, daily_limit: Number(e.target.value) })}
                        className="bg-surface border-border focus:border-brand-accent"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="weeklyLimit" className="text-foreground text-sm font-medium">
                        Weekly Limit (£)
                      </Label>
                      <Input 
                        id="weeklyLimit" 
                        type="number"
                        min="0"
                        step="50"
                        placeholder="0 = No limit"
                        value={limits.weekly_limit || ''}
                        onChange={(e) => setLimits({ ...limits, weekly_limit: Number(e.target.value) })}
                        className="bg-surface border-border focus:border-brand-accent"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="monthlyLimit" className="text-foreground text-sm font-medium">
                        Monthly Limit (£)
                      </Label>
                      <Input 
                        id="monthlyLimit" 
                        type="number"
                        min="0"
                        step="100"
                        placeholder="0 = No limit"
                        value={limits.monthly_limit || ''}
                        onChange={(e) => setLimits({ ...limits, monthly_limit: Number(e.target.value) })}
                        className="bg-surface border-border focus:border-brand-accent"
                      />
                    </div>
                  </div>
                  
                  <Button 
                    onClick={handleSetLimits}
                    disabled={updateLimitsMutation.isPending}
                    className="bg-yellow-500 hover:bg-yellow-600 text-black"
                  >
                    {updateLimitsMutation.isPending ? "Saving..." : "Save Spending Limits"}
                  </Button>
                </div>

                {/* Reality Check */}
                <div className="pt-4 border-t border-border">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <Label className="text-foreground text-sm font-medium">Reality Check Notifications</Label>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        Get reminders every 30 minutes about your betting activity
                      </p>
                    </div>
                    <Switch />
                  </div>
                </div>

                {/* Loss Chasing Alert */}
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Loss Chasing Alerts</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      MAX will warn you if it detects loss chasing behavior
                    </p>
                  </div>
                  <Switch defaultChecked />
                </div>

                {/* Self-Exclusion Warning */}
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                    <div className="space-y-2 flex-1">
                      <h4 className="font-semibold text-foreground">Need a Break?</h4>
                      <p className="text-sm text-muted-foreground">
                        If you feel you need time away from betting, you can request self-exclusion. 
                        This will lock your account for a period you choose.
                      </p>
                      <Button 
                        variant="outline"
                        className="border-red-500 text-red-500 hover:bg-red-500/10"
                        size="sm"
                      >
                        Request Self-Exclusion
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Resources */}
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                  <h4 className="font-semibold text-foreground mb-2">Need Help?</h4>
                  <p className="text-sm text-muted-foreground mb-3">
                    If you're concerned about your gambling, support is available:
                  </p>
                  <div className="space-y-2 text-sm">
                    <a href="https://www.gamcare.org.uk" target="_blank" rel="noopener noreferrer" 
                       className="block text-blue-400 hover:underline">
                      • GamCare: 0808 8020 133
                    </a>
                    <a href="https://www.begambleaware.org" target="_blank" rel="noopener noreferrer"
                       className="block text-blue-400 hover:underline">
                      • BeGambleAware
                    </a>
                    <a href="https://www.gamblersanonymous.org.uk" target="_blank" rel="noopener noreferrer"
                       className="block text-blue-400 hover:underline">
                      • Gamblers Anonymous
                    </a>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Preferences */}
            <Card className="bg-card border-card-border shadow-card">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-foreground text-lg sm:text-xl">
                  <div className="w-8 h-8 bg-brand-primary/20 rounded-lg flex items-center justify-center">
                    <Globe className="w-4 h-4 text-brand-accent" />
                  </div>
                  Preferences
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Dark Mode</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">Toggle between light and dark themes</p>
                  </div>
                  <Switch />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label className="text-foreground text-sm font-medium">Auto-Refresh Data</Label>
                    <p className="text-xs sm:text-sm text-muted-foreground">Automatically update predictions and statistics</p>
                  </div>
                  <Switch />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Settings;