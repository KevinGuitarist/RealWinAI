import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Target, Info, Star, Shield } from "lucide-react";

const Index = () => {
  const features = [
    {
      icon: Target,
      title: "98.7% Accuracy",
      description: "Our AI analyzes over 1000+ data points per match to deliver the most accurate predictions in the industry."
    },
    {
      icon: Info,
      title: "Real-Time Analysis", 
      description: "Get instant predictions with live odds updates and in-play betting opportunities."
    },
    {
      icon: Star,
      title: "Proven Results",
      description: "Over $2.3M in winnings generated for our users in the last 12 months alone."
    },
    {
      icon: Shield,
      title: "Risk Management",
      description: "Built-in bankroll management tools to protect your capital and maximize long-term profits."
    }
  ];

  const recentResults = [
    {
      match: "Man City vs Arsenal",
      prediction: "OVER 2.5",
      result: "Final: 3-1 ✓",
      profit: "+$1,247 profit"
    },
    {
      match: "India vs Australia", 
      prediction: "INDIA WIN",
      result: "India won by 6 wickets ✓",
      profit: "+$892 profit"
    },
    {
      match: "Liverpool vs Chelsea",
      prediction: "BTTS", 
      result: "Final: 2-1 ✓",
      profit: "+$634 profit"
    }
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="px-4 sm:px-6 py-4 border-b border-border">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <img 
            src="https://realwin.ai/static/images/logo-transparent.png" 
            alt="RealWin.AI" 
            className="h-6 sm:h-8"
          />
          <Button 
            asChild
            className="bg-[#9AFF00] hover:bg-[#8AEF00] text-black font-bold px-4 sm:px-6 py-2 rounded-lg text-sm sm:text-base"
          >
            <a href="/login">LOGIN</a>
          </Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="px-4 sm:px-6 py-12 sm:py-20">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              
              <div className="space-y-6">
                <h1 className="text-3xl sm:text-4xl lg:text-6xl font-bold text-foreground leading-tight">
                  Join <span className="text-brand-accent">18,750+</span><br />
                  Members Already<br />
                  Winning with<br />
                  RealWin AI
                </h1>
                
                <p className="text-lg sm:text-xl text-muted-foreground">
                  Smarter football & cricket predictions powered by AI. Trusted by thousands who win daily.
                </p>
              </div>

              <div className="space-y-3 sm:space-y-4">
                <div className="space-y-2">
                  <h3 className="text-base sm:text-lg font-semibold text-brand-accent">Start Your Free 3-Day Trial Today</h3>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xl sm:text-2xl font-bold text-muted-foreground line-through">£19.99</span>
                    <span className="text-2xl sm:text-3xl font-bold text-brand-accent">£0</span>
                    <span className="text-xs sm:text-sm text-muted-foreground">- No CREDIT CARD NEEDED</span>
                  </div>
                </div>
                
                <p className="text-xs sm:text-sm text-brand-accent">Only 35 free trials left this week</p>
                
                <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
                  <Button 
                    asChild
                    size="lg"
                    className="gradient-brand hover:opacity-90 transition-opacity px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg font-semibold"
                  >
                    <a href="/signup">START WINNING NOW</a>
                  </Button>
                </div>

                <div className="space-y-2">
                  <Input 
                    type="email" 
                    placeholder="Email*" 
                    className="bg-surface border-border text-sm sm:text-base"
                  />
                  <p className="text-xs sm:text-sm text-muted-foreground">Get your 3-day free trial with accurate predictions</p>
                </div>
              </div>
            </div>
            
            <div className="flex justify-center order-1 lg:order-2">
              <img 
                src="https://realwin.ai/static/images/homebg1.png" 
                alt="AI Sports Dashboard" 
                className="max-w-full h-auto rounded-lg w-full max-w-md lg:max-w-full"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose RealWin Section */}
      <section className="px-4 sm:px-6 py-12 sm:py-20 bg-surface/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-center text-brand-accent mb-8 sm:mb-12">
            Why Choose RealWin?
          </h2>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="bg-card border-card-border shadow-card">
                <CardContent className="p-6 text-center space-y-4">
                  <div className="w-12 h-12 rounded-full bg-brand-primary/20 flex items-center justify-center mx-auto">
                    <feature.icon className="w-6 h-6 text-brand-accent" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl lg:text-4xl font-bold text-center text-brand-accent mb-12">
            How It Works
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-brand-primary text-background flex items-center justify-center mx-auto text-xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold text-foreground">Register for free now</h3>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-brand-primary text-background flex items-center justify-center mx-auto text-xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold text-foreground">Unlock today's AI best tips</h3>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-brand-primary text-background flex items-center justify-center mx-auto text-xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold text-foreground">Build profits over time</h3>
            </div>
          </div>

          <div className="text-center mt-12 space-y-4">
            <Input 
              type="email" 
              placeholder="Email*" 
              className="max-w-md mx-auto bg-surface border-border"
            />
            <p className="text-sm text-muted-foreground">Get your 3-day free trial with accurate predictions</p>
          </div>
        </div>
      </section>

      {/* Recent Results Section */}
      <section className="px-6 py-20 bg-surface/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl lg:text-4xl font-bold text-center text-brand-accent mb-12">
            Recent Results
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {recentResults.map((result, index) => (
              <Card key={index} className="bg-card border-card-border shadow-card">
                <CardContent className="p-6 space-y-3">
                  <h3 className="font-semibold text-foreground">{result.match}</h3>
                  <div className="bg-brand-primary/20 text-brand-accent px-3 py-1 rounded-full text-sm font-medium inline-block">
                    {result.prediction}
                  </div>
                  <p className="text-sm text-muted-foreground">{result.result}</p>
                  <p className="text-lg font-bold text-brand-accent">{result.profit}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Index;
