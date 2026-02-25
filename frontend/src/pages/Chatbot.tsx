import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, Send, BarChart3, TrendingUp, Activity } from "lucide-react";
import { useState } from "react";

const Chatbot = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      type: "bot",
      content: "Hello! I'm your RealWin AI Expert. I can help you with sports predictions, player statistics, team analysis, and match insights for Football, Cricket, and more. What would you like to know?"
    }
  ]);

  const handleSendMessage = () => {
    if (!message.trim()) return;
    
    setMessages(prev => [...prev, { type: "user", content: message }]);
    
    // Simulate bot response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        type: "bot",
        content: "I'm processing your request for sports analysis. Advanced AI features are coming soon to provide detailed insights for Football, Cricket, and more sports."
      }]);
    }, 1000);
    
    setMessage("");
  };

  const quickActions = [
    { 
      icon: BarChart3, 
      title: "Match Predictions", 
      description: "Get AI-powered predictions for upcoming matches",
      action: "Show me today's match predictions"
    },
    { 
      icon: TrendingUp, 
      title: "Player Stats", 
      description: "Analyze player performance and recent form",
      action: "Analyze top players this season"
    },
    { 
      icon: Activity, 
      title: "Team Analysis", 
      description: "Deep dive into team statistics and head-to-head records",
      action: "Compare team performances in recent matches"
    }
  ];

  const handleQuickAction = (action: string) => {
    setMessages(prev => [...prev, { type: "user", content: action }]);
    setTimeout(() => {
      setMessages(prev => [...prev, {
        type: "bot",
        content: "I'm processing your request for sports analysis. Advanced AI features are coming soon to provide detailed insights for Football, Cricket, and more sports."
      }]);
    }, 1000);
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-3 sm:p-6">
        <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6">
          {/* Header */}
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center gap-2">
              <Bot className="w-6 h-6 sm:w-8 sm:h-8 text-brand-accent" />
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">RealWin AI Expert</h1>
            </div>
            <p className="text-sm sm:text-base text-muted-foreground px-4">
              Your intelligent assistant for sports predictions, statistics, and data analysis
            </p>
          </div>

          <div className="grid lg:grid-cols-4 gap-4 sm:gap-6">
            {/* Quick Actions */}
            <div className="lg:col-span-1 space-y-4">
              <h2 className="text-base sm:text-lg font-semibold text-foreground">Quick Actions</h2>
              {quickActions.map((action, index) => (
                <Card key={index} className="bg-card border-card-border shadow-card cursor-pointer hover:shadow-brand transition-shadow">
                  <CardContent className="p-3 sm:p-4" onClick={() => handleQuickAction(action.action)}>
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 sm:w-10 sm:h-10 bg-brand-primary/20 rounded-lg flex items-center justify-center flex-shrink-0">
                        <action.icon className="w-4 h-4 sm:w-5 sm:h-5 text-brand-accent" />
                      </div>
                      <div className="space-y-1 min-w-0 flex-1">
                        <h3 className="font-medium text-foreground text-sm sm:text-base">{action.title}</h3>
                        <p className="text-xs sm:text-sm text-muted-foreground">{action.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Chat Interface */}
            <div className="lg:col-span-3">
              <Card className="bg-card border-card-border shadow-card h-[400px] sm:h-[500px] lg:h-[600px] flex flex-col">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center gap-2 text-foreground text-base sm:text-lg">
                    <Bot className="w-4 h-4 sm:w-5 sm:h-5 text-brand-accent" />
                    Sports AI Assistant
                  </CardTitle>
                </CardHeader>
                
                <CardContent className="flex-1 flex flex-col p-3 sm:p-6 pt-0">
                  {/* Messages */}
                  <ScrollArea className="flex-1 mb-3 sm:mb-4">
                    <div className="space-y-3 sm:space-y-4 pr-2">
                      {messages.map((msg, index) => (
                        <div
                          key={index}
                          className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-[85%] sm:max-w-[80%] rounded-lg p-2 sm:p-3 ${
                              msg.type === 'user'
                                ? 'bg-brand-primary text-background rounded-br-sm'
                                : 'bg-surface text-foreground rounded-bl-sm'
                            }`}
                          >
                            <p className="text-xs sm:text-sm leading-relaxed">{msg.content}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>

                  {/* Input */}
                  <div className="flex gap-2">
                    <Input
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Ask about sports predictions, stats, or analysis..."
                      className="bg-surface border-border text-sm"
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    />
                    <Button 
                      onClick={handleSendMessage}
                      className="bg-brand-primary hover:bg-brand-primary-hover text-background hover:text-background px-3 sm:px-4"
                    >
                      <Send className="w-3 h-3 sm:w-4 sm:h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Chatbot;