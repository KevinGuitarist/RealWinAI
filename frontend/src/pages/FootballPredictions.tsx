import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Trophy, ArrowLeft, Loader2 } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { getFootballPredictions } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface FootballPrediction {
  id: number;
  key: string;
  match_name: string;
  match_kick_off: string;
  predicted_winner: string;
  win_probability_percent: number;
  prediction_object: any;
  logos?: {
    team_a: string;
    team_b: string;
  };
}

const FootballPredictions = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [predictions, setPredictions] = useState<FootballPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  const getCurrentDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0]; // Format: YYYY-MM-DD
  };

  const loadPredictions = async (forceRefresh = false) => {
    try {
      setLoading(true);
      const currentDate = getCurrentDate();
      
      // Fetch from API and save to cache
      const data = await getFootballPredictions(currentDate);
      setPredictions(data);
      // Save to localStorage for details page access  
      localStorage.setItem('footballPredictionsData', JSON.stringify(data));
      
    } catch (error) {
      console.error("Error fetching predictions:", error);
      toast({
        title: "Error",
        description: "Failed to load football predictions. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshPredictions = () => {
    loadPredictions(true);
  };

  useEffect(() => {
    // Initial load
    loadPredictions();
  }, []);

  const filteredPredictions = predictions.filter(prediction =>
    prediction.match_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewAnalysis = (prediction: FootballPrediction) => {
    // Store the prediction data in localStorage for the football analysis page
    localStorage.setItem(`football_analysis_${prediction.id}`, JSON.stringify(prediction));
    navigate(`/football-analysis/${prediction.id}`);
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-3 sm:p-6">
        <div className="max-w-4xl mx-auto space-y-6 sm:space-y-8">
          {/* Back Button */}
          <Button 
            variant="outline" 
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 border-border text-muted-foreground hover:text-black text-sm sm:text-base"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Button>

          {/* Header */}
          <div className="text-center space-y-3 sm:space-y-4">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-foreground">Football Predictions</h1>
            <p className="text-base sm:text-lg text-muted-foreground px-4">
              Get today's top football predictions with advanced analytics!
            </p>
          </div>

          {/* Search Section */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-center">
            <Input
              placeholder="Search football matches by team or venue..."
              className="flex-1 bg-surface border-border text-sm sm:text-base"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Button 
              onClick={refreshPredictions}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold hover:text-white text-sm sm:text-base"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Refreshing...
                </>
              ) : (
                "Refresh"
              )}
            </Button>
          </div>

          {/* Today's Predictions Header */}
          <div className="bg-blue-600 rounded-lg p-4 sm:p-6 text-center">
            <h2 className="text-xl sm:text-2xl font-bold text-brand-accent">
              Today's Football Predictions
            </h2>
          </div>

          {/* Stake Logo Section */}
          <div className="flex justify-center">
            <div className="bg-surface rounded-lg p-6 border border-border">
              <a 
                href="http://stake.com/?c=nWx49aci" 
                target="_blank" 
                rel="noopener noreferrer"
                className="cursor-pointer"
              >
                <img 
                  src="https://realwin.ai/static/images/banner-3.png" 
                  alt="Stake" 
                  className="h-20 max-w-full hover:opacity-80 transition-opacity"
                />
              </a>
            </div>
          </div>

          {/* Predictions List */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-4">
                <Loader2 className="w-8 h-8 animate-spin text-brand-primary mx-auto" />
                <p className="text-muted-foreground">Loading football predictions...</p>
              </div>
            </div>
          ) : filteredPredictions.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground text-lg">
                {searchTerm ? "No matches found for your search." : "No football predictions available for today."}
              </p>
            </div>
          ) : (
            <div className="space-y-4 sm:space-y-6">
              {filteredPredictions.map((prediction) => (
                <Card key={prediction.id} className="bg-card border-card-border shadow-card">
                  <CardContent className="p-4 sm:p-6">
                    <div className="space-y-3 sm:space-y-4">
                      {/* Match Title */}
                      <h3 className="text-lg sm:text-xl font-bold text-foreground">
                        {prediction.match_name}
                      </h3>

                      {/* Predicted Winner */}
                      <div className="flex items-center gap-2 bg-surface rounded-lg p-3">
                        <Trophy className="w-4 h-4 sm:w-5 sm:h-5 text-brand-accent flex-shrink-0" />
                        <span className="text-brand-accent font-semibold text-sm sm:text-base">
                          Predicted Winner: {prediction.predicted_winner}
                        </span>
                      </div>

                      {/* Match Details */}
                      <div className="space-y-4">
                        {/* Basic Match Info */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <p className="text-xs sm:text-sm text-muted-foreground">
                              <span className="font-medium">Kick Off: </span>
                              {new Date(prediction.match_kick_off).toLocaleString()}
                            </p>
                          </div>
                          <div className="space-y-2">
                            <div className="text-xs sm:text-sm text-muted-foreground">
                              <span className="font-medium">Win Probability: </span>
                              {prediction.win_probability_percent}%
                            </div>
                            <Progress 
                              value={prediction.win_probability_percent} 
                              className="w-full h-2"
                            />
                          </div>
                        </div>

                        {/* Key Analysis Points */}
                        {prediction.prediction_object && (
                          <div className="bg-surface/50 rounded-lg p-4 space-y-3">
                            <h4 className="font-semibold text-foreground text-sm">Key Analysis Points:</h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs sm:text-sm">
                              {prediction.prediction_object.form_analysis && (
                                <div>
                                  <span className="font-medium text-muted-foreground">Form: </span>
                                  <span className="text-foreground">{prediction.prediction_object.form_analysis}</span>
                                </div>
                              )}
                              {prediction.prediction_object.head_to_head && (
                                <div>
                                  <span className="font-medium text-muted-foreground">H2H: </span>
                                  <span className="text-foreground">{prediction.prediction_object.head_to_head}</span>
                                </div>
                              )}
                              {prediction.prediction_object.injury_news && (
                                <div>
                                  <span className="font-medium text-muted-foreground">Injuries: </span>
                                  <span className="text-foreground">{prediction.prediction_object.injury_news}</span>
                                </div>
                              )}
                              {prediction.prediction_object.weather_impact && (
                                <div>
                                  <span className="font-medium text-muted-foreground">Weather: </span>
                                  <span className="text-foreground">{prediction.prediction_object.weather_impact}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        <Button 
                          className="bg-brand-primary hover:bg-brand-primary-hover text-background font-semibold hover:text-background w-full sm:w-auto text-sm sm:text-base"
                          onClick={() => handleViewAnalysis(prediction)}
                        >
                          View Complete Analysis
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default FootballPredictions;