import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Slider } from "@/components/ui/slider";
import { useToast } from "@/hooks/use-toast";
import { createStrategy } from "@/lib/api";
import { getCurrentUser } from "@/lib/auth";
import { Target, Shield, TrendingUp, AlertCircle, CheckCircle } from "lucide-react";

const StrategySetup = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const user = getCurrentUser();

  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    bankroll: 1000,
    riskProfile: 'moderate',
    targetMonthlyProfit: 100,
    acceptableDrawdown: 15,
    timeHorizon: '3-6 months',
    preferences: {
      favoriteSports: [] as string[],
      preferredMarkets: [] as string[],
      maxBetsPerDay: 3,
    }
  });

  const createStrategyMutation = useMutation({
    mutationFn: () => createStrategy(user?.id || 0, {
      bankroll: formData.bankroll,
      goals: {
        target_monthly_profit: formData.targetMonthlyProfit,
        acceptable_drawdown: formData.acceptableDrawdown,
        time_horizon: formData.timeHorizon,
      },
      risk_profile: formData.riskProfile,
      preferences: formData.preferences,
    }),
    onSuccess: () => {
      toast({
        title: "Strategy Created!",
        description: "Your personalized betting strategy has been set up successfully.",
      });
      navigate('/dashboard');
    },
    onError: () => {
      toast({
        title: "Error",
        description: "Failed to create strategy. Please try again.",
        variant: "destructive",
      });
    }
  });

  const handleSubmit = () => {
    createStrategyMutation.mutate();
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-3 sm:p-6">
        <div className="max-w-3xl mx-auto space-y-4 sm:space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Target className="w-6 h-6 sm:w-8 sm:h-8 text-brand-accent" />
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">
                Create Your Betting Strategy
              </h1>
            </div>
            <p className="text-sm sm:text-base text-muted-foreground">
              Let MAX personalize betting recommendations based on your goals and risk tolerance
            </p>
          </div>

          {/* Progress Indicator */}
          <div className="flex items-center justify-center gap-2">
            {[1, 2, 3].map((s) => (
              <div key={s} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  s === step ? 'bg-brand-primary text-white' : 
                  s < step ? 'bg-green-500 text-white' : 'bg-surface text-muted-foreground'
                }`}>
                  {s < step ? <CheckCircle className="w-4 h-4" /> : s}
                </div>
                {s < 3 && <div className={`w-12 h-0.5 ${s < step ? 'bg-green-500' : 'bg-surface'}`} />}
              </div>
            ))}
          </div>

          {/* Step 1: Bankroll & Goals */}
          {step === 1 && (
            <Card className="bg-card border-card-border shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Bankroll & Goals
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="bankroll">Initial Bankroll (£)</Label>
                  <Input
                    id="bankroll"
                    type="number"
                    value={formData.bankroll}
                    onChange={(e) => setFormData({ ...formData, bankroll: Number(e.target.value) })}
                    min={100}
                    step={100}
                  />
                  <p className="text-xs text-muted-foreground">
                    The total amount you're willing to allocate for betting
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="targetProfit">Target Monthly Profit (£)</Label>
                  <Input
                    id="targetProfit"
                    type="number"
                    value={formData.targetMonthlyProfit}
                    onChange={(e) => setFormData({ ...formData, targetMonthlyProfit: Number(e.target.value) })}
                    min={0}
                    step={10}
                  />
                  <p className="text-xs text-muted-foreground">
                    Realistic profit goal: {((formData.targetMonthlyProfit / formData.bankroll) * 100).toFixed(1)}% ROI
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Time Horizon</Label>
                  <RadioGroup
                    value={formData.timeHorizon}
                    onValueChange={(value) => setFormData({ ...formData, timeHorizon: value })}
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="1-3 months" id="short" />
                      <Label htmlFor="short">1-3 months</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="3-6 months" id="medium" />
                      <Label htmlFor="medium">3-6 months</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="6-12 months" id="long" />
                      <Label htmlFor="long">6-12 months</Label>
                    </div>
                  </RadioGroup>
                </div>

                <Button 
                  onClick={() => setStep(2)} 
                  className="w-full bg-brand-primary hover:bg-brand-primary-hover"
                >
                  Next: Risk Profile
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Step 2: Risk Profile */}
          {step === 2 && (
            <Card className="bg-card border-card-border shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5" />
                  Risk Profile
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <Label>Select Your Risk Tolerance</Label>
                  <RadioGroup
                    value={formData.riskProfile}
                    onValueChange={(value) => setFormData({ ...formData, riskProfile: value })}
                  >
                    <Card className={`cursor-pointer ${formData.riskProfile === 'conservative' ? 'border-brand-primary' : ''}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="conservative" id="conservative" />
                          <Label htmlFor="conservative" className="cursor-pointer flex-1">
                            <div>
                              <p className="font-semibold">Conservative</p>
                              <p className="text-xs text-muted-foreground">
                                Low risk, steady growth. Max 2-3% stake per bet.
                              </p>
                            </div>
                          </Label>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className={`cursor-pointer ${formData.riskProfile === 'moderate' ? 'border-brand-primary' : ''}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="moderate" id="moderate" />
                          <Label htmlFor="moderate" className="cursor-pointer flex-1">
                            <div>
                              <p className="font-semibold">Moderate</p>
                              <p className="text-xs text-muted-foreground">
                                Balanced approach. Max 5% stake per bet.
                              </p>
                            </div>
                          </Label>
                        </div>
                      </CardContent>
                    </Card>

                    <Card className={`cursor-pointer ${formData.riskProfile === 'aggressive' ? 'border-brand-primary' : ''}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="aggressive" id="aggressive" />
                          <Label htmlFor="aggressive" className="cursor-pointer flex-1">
                            <div>
                              <p className="font-semibold">Aggressive</p>
                              <p className="text-xs text-muted-foreground">
                                Higher risk, higher rewards. Max 8-10% stake per bet.
                              </p>
                            </div>
                          </Label>
                        </div>
                      </CardContent>
                    </Card>
                  </RadioGroup>
                </div>

                <div className="space-y-2">
                  <Label>Acceptable Drawdown: {formData.acceptableDrawdown}%</Label>
                  <Slider
                    value={[formData.acceptableDrawdown]}
                    onValueChange={([value]) => setFormData({ ...formData, acceptableDrawdown: value })}
                    min={5}
                    max={30}
                    step={5}
                  />
                  <p className="text-xs text-muted-foreground">
                    Maximum loss you can tolerate before pausing betting
                  </p>
                </div>

                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setStep(1)}
                    className="flex-1"
                  >
                    Back
                  </Button>
                  <Button 
                    onClick={() => setStep(3)}
                    className="flex-1 bg-brand-primary hover:bg-brand-primary-hover"
                  >
                    Next: Preferences
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 3: Preferences */}
          {step === 3 && (
            <Card className="bg-card border-card-border shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5" />
                  Betting Preferences
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <Label>Maximum Bets Per Day</Label>
                  <Slider
                    value={[formData.preferences.maxBetsPerDay]}
                    onValueChange={([value]) => setFormData({ 
                      ...formData, 
                      preferences: { ...formData.preferences, maxBetsPerDay: value }
                    })}
                    min={1}
                    max={10}
                    step={1}
                  />
                  <p className="text-sm text-foreground">
                    {formData.preferences.maxBetsPerDay} bet{formData.preferences.maxBetsPerDay > 1 ? 's' : ''} per day
                  </p>
                </div>

                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                    <div className="space-y-1">
                      <p className="text-sm font-medium text-foreground">Strategy Summary</p>
                      <ul className="text-xs text-muted-foreground space-y-1">
                        <li>• Bankroll: £{formData.bankroll}</li>
                        <li>• Risk Profile: {formData.riskProfile}</li>
                        <li>• Target Profit: £{formData.targetMonthlyProfit}/month</li>
                        <li>• Max Drawdown: {formData.acceptableDrawdown}%</li>
                        <li>• Max Bets/Day: {formData.preferences.maxBetsPerDay}</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setStep(2)}
                    className="flex-1"
                  >
                    Back
                  </Button>
                  <Button 
                    onClick={handleSubmit}
                    disabled={createStrategyMutation.isPending}
                    className="flex-1 bg-brand-primary hover:bg-brand-primary-hover"
                  >
                    {createStrategyMutation.isPending ? "Creating..." : "Create Strategy"}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Info Card */}
          <Card className="bg-surface border-border">
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground text-center">
                MAX will use this strategy to recommend bet sizes and suggest opportunities that match your goals and risk tolerance. You can update your strategy anytime from settings.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default StrategySetup;
