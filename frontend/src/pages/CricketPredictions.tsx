import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Trophy, ArrowLeft, Loader2 } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { getCricketPredictions } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

const CricketPredictions = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [predictions, setPredictions] = useState([]);
  const [filteredPredictions, setFilteredPredictions] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchPredictions = async (forceRefresh = false) => {
    try {
      setLoading(true);
      const today = new Date().toISOString().split('T')[0];
      
      console.log('Fetching cricket predictions for date:', today);
      console.log('Force refresh:', forceRefresh);

      console.log('Making API call to get cricket predictions...');
      const data = await getCricketPredictions(today);
      console.log('Cricket predictions received:', data);
      console.log('Number of matches:', data?.length || 0);
      
      setPredictions(data);
      setFilteredPredictions(data);
      // Save to localStorage for details page access
      localStorage.setItem('cricketPredictionsData', JSON.stringify(data));
    } catch (error) {
      console.error('Error fetching cricket predictions:', error);
      toast({
        title: "Error",
        description: "Failed to fetch cricket predictions",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const refreshPredictions = () => {
    fetchPredictions(true);
  };

  useEffect(() => {
    // Initial fetch
    fetchPredictions();
  }, [toast]);

  useEffect(() => {
    const filtered = predictions.filter((prediction) =>
      prediction.match_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      prediction.predicted_winner.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredPredictions(filtered);
  }, [searchTerm, predictions]);

  const formatMatchTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric', 
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const handleViewAnalysis = (matchIndex: number) => {
    navigate(`/cricket-details/${matchIndex}`);
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Back Button */}
          <Button 
            variant="outline" 
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 border-border text-muted-foreground hover:text-background"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Button>

          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold text-foreground">Cricket Predictions</h1>
            <p className="text-lg text-muted-foreground">
              Click the button below to view today's detailed Cricket predictions and past results.
            </p>
          </div>

          {/* Search Section */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-center max-w-md mx-auto">
            <Input
              placeholder="Search cricket matches by team or venue..."
              className="flex-1 bg-surface border-border"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <Button 
              onClick={refreshPredictions}
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold hover:text-white"
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
          <div className="bg-blue-600 rounded-lg p-6 text-center">
            <h2 className="text-2xl font-bold text-brand-accent">
              Today's Cricket Predictions
            </h2>
          </div>

          {/* Stake Logo Section */}
          <div className="flex justify-center">
            <div className="bg-surface rounded-lg p-6 border border-border">
              <a 
                href="https://stake.games/?offer=realwin&c=Realwinai" 
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
          <div className="space-y-6">
            {loading ? (
              <div className="text-center py-8">
                <div className="text-muted-foreground">Loading predictions...</div>
              </div>
            ) : filteredPredictions.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-muted-foreground">
                  No matches found for your search.
                  <br />
                  <small>Total predictions: {predictions.length}, Filtered: {filteredPredictions.length}</small>
                  <br />
                  <small>Search term: "{searchTerm}"</small>
                </div>
              </div>
            ) : (
              filteredPredictions.map((prediction, index) => (
                <Card key={index} className="bg-card border-card-border shadow-card">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      {/* Match Title */}
                      <h3 className="text-xl font-bold text-foreground">
                        {prediction.match_name}
                      </h3>

                      {/* Predicted Winner */}
                      <div className="flex items-center gap-2 bg-surface rounded-lg p-3">
                        <Trophy className="w-5 h-5 text-brand-accent" />
                        <span className="text-brand-accent font-semibold">
                          Predicted Winner: {prediction.predicted_winner}
                        </span>
                      </div>

                      {/* Match Details */}
                      <div className="space-y-4">
                        {/* Basic Match Info */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div className="space-y-2">
                            <p className="text-sm text-muted-foreground">
                              <span className="font-medium">Match Start: </span>
                              {formatMatchTime(prediction.match_kick_off)}
                            </p>
                          </div>
                          <div className="space-y-2">
                            <div className="text-sm text-muted-foreground">
                              <span className="font-medium">Win Probability: </span>
                              {prediction.win_probability}%
                            </div>
                            <Progress 
                              value={prediction.win_probability} 
                              className="w-full h-2"
                            />
                          </div>
                        </div>

                        {/* Key Analysis Points */}
                        {prediction.prediction_object && (
                          <div className="bg-surface/50 rounded-lg p-4 space-y-3">
                            <h4 className="font-semibold text-foreground text-sm">Key Analysis Points:</h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                              {prediction.prediction_object.team_form && (
                                <div>
                                  <span className="font-medium text-muted-foreground">Team Form: </span>
                                  <span className="text-foreground">{prediction.prediction_object.team_form}</span>
                                </div>
                              )}
                              {prediction.prediction_object.pitch_conditions && (
                                <div>
                                  <span className="font-medium text-muted-foreground">Pitch: </span>
                                  <span className="text-foreground">{prediction.prediction_object.pitch_conditions}</span>
                                </div>
                              )}
                              {prediction.prediction_object.key_players && (
                                <div>
                                  <span className="font-medium text-muted-foreground">Key Players: </span>
                                  <span className="text-foreground">{prediction.prediction_object.key_players}</span>
                                </div>
                              )}
                              {prediction.prediction_object.weather_forecast && (
                                <div>
                                  <span className="font-medium text-muted-foreground">Weather: </span>
                                  <span className="text-foreground">{prediction.prediction_object.weather_forecast}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        <Button 
                          className="bg-brand-primary hover:bg-brand-primary-hover text-background font-semibold hover:text-background w-full sm:w-auto"
                          onClick={() => handleViewAnalysis(index)}
                        >
                          View Complete Analysis
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default CricketPredictions;