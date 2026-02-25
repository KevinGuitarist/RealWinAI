import { SportCard } from "./SportCard";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

export function DashboardContent() {
  const navigate = useNavigate();

  const handleSportSelect = (sport: string) => {
    if (sport === "football") {
      navigate("/football-predictions");
    } else if (sport === "cricket") {
      navigate("/cricket-predictions");
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex justify-center mb-4">
          <img 
            src="/favicon.png" 
            alt="RealWin.AI" 
            className="h-16 w-auto"
          />
        </div>
        <h1 className="text-5xl font-bold text-white">
          AI and Data Driven Sports Predictions
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Choose your sport to get advanced AI-powered predictions with real-time data
        </p>
      </div>
      
      {/* Sports Cards */}
      <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        <SportCard
          icon={<img src="https://realwin.ai/static/images/football.png" alt="Football" className="w-8 h-8" />}
          title="Football"
          description="Advanced football predictions using analytics & AI"
          features={[
            "Team form analysis",
            "Head-to-head statistics",
            "Player performance metrics",
            "Weather & pitch conditions"
          ]}
          onClick={() => handleSportSelect("football")}
        />
        
        <SportCard
          icon={<img src="https://realwin.ai/static/images/cricket.png" alt="Cricket" className="w-8 h-8" />}
          title="Cricket"
          description="Comprehensive cricket analysis with format-specific insights"
          features={[
            "Match format analysis (T20, ODI, Test)",
            "Player form & conditions",
            "Pitch reports & weather",
            "Historical performance data"
          ]}
          onClick={() => handleSportSelect("cricket")}
        />
      </div>
    </div>
  );
}