import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, Eye } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useNavigate, useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

const CricketDetails = () => {
  const navigate = useNavigate();
  const { matchId } = useParams();
  const [matchData, setMatchData] = useState(null);

  useEffect(() => {
    // Get data from localStorage
    const storedData = localStorage.getItem('cricketPredictionsData');
    console.log('CricketDetails - matchId:', matchId);
    console.log('CricketDetails - storedData:', storedData);
    
    if (storedData) {
      const predictions = JSON.parse(storedData);
      console.log('CricketDetails - predictions:', predictions);
      const matchIndex = parseInt(matchId);
      console.log('CricketDetails - matchIndex:', matchIndex);
      console.log('CricketDetails - predictions[matchIndex]:', predictions[matchIndex]);
      
      if (predictions[matchIndex]) {
        setMatchData(predictions[matchIndex]);
      }
    }
  }, [matchId]);

  const formatMatchTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  if (!matchData) {
    return (
      <DashboardLayout>
        <div className="min-h-screen bg-background p-6">
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="text-center py-8">
              <div className="text-muted-foreground">Loading match details...</div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Go Back Button */}
          <Button 
            variant="outline" 
            onClick={() => navigate('/cricket-predictions')}
            className="flex items-center gap-2 bg-brand-primary text-background hover:bg-brand-primary-hover hover:text-background border-brand-primary"
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </Button>

          {/* Match Header Card */}
          <Card className="bg-card border-card-border shadow-card">
            <CardContent className="p-6">
              <div className="text-center space-y-4">
                <div className="flex items-center justify-center space-x-8">
                  <div className="text-center">
                    <p className="font-semibold text-foreground text-lg">{matchData.prediction_object.teams.a_name}</p>
                    <p className="text-sm text-muted-foreground">({matchData.prediction_object.teams.a_code})</p>
                  </div>
                  
                  <div className="text-center">
                    <span className="text-2xl font-bold text-muted-foreground">VS</span>
                  </div>
                  
                  <div className="text-center">
                    <p className="font-semibold text-foreground text-lg">{matchData.prediction_object.teams.b_name}</p>
                    <p className="text-sm text-muted-foreground">({matchData.prediction_object.teams.b_code})</p>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <h3 className="text-lg font-semibold text-muted-foreground">Prediction</h3>
                  <p className="text-xl font-bold text-brand-accent">{matchData.predicted_winner} TO WIN</p>
                  <div className="w-full bg-surface rounded-full h-3 mt-2">
                    <div 
                      className="bg-brand-primary h-3 rounded-full" 
                      style={{ width: `${matchData.win_probability}%` }}
                    ></div>
                  </div>
                  <p className="text-sm text-muted-foreground">Win Probability {matchData.win_probability}%</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tournament & Format Info */}
          <Card className="bg-card border-card-border shadow-card">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">MATCH: {matchData.match_name}</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <span className="font-semibold text-foreground">Tournament: </span>
                  <span className="text-muted-foreground">{matchData.prediction_object.match_metadata?.tournament || "N/A"}</span>
                </div>
                
                <div>
                  <span className="font-semibold text-foreground">Format: </span>
                  <span className="text-muted-foreground capitalize">{matchData.prediction_object.match_metadata?.format || "N/A"}</span>
                </div>
                
                <div>
                  <span className="font-semibold text-foreground">Confidence: </span>
                  <span className="text-muted-foreground capitalize">{matchData.prediction_object.confidence}</span>
                </div>
                
                <div>
                  <span className="font-semibold text-foreground">Venue: </span>
                  <span className="text-muted-foreground">{matchData.venue || "N/A"}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Key Players */}
          <Card className="bg-card border-card-border shadow-card">
            <CardContent className="p-6">
              <h4 className="font-semibold text-foreground mb-4">Key Players</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h5 className="font-semibold text-foreground mb-2">{matchData.prediction_object.teams.a_name}</h5>
                  <ul className="space-y-1">
                    {matchData.prediction_object.supporting.key_players_a?.map((player, index) => (
                      <li key={index} className="text-muted-foreground">• {player}</li>
                    )) || <li className="text-muted-foreground">No key players listed</li>}
                  </ul>
                </div>
                <div>
                  <h5 className="font-semibold text-foreground mb-2">{matchData.prediction_object.teams.b_name}</h5>
                  <ul className="space-y-1">
                    {matchData.prediction_object.supporting.key_players_b?.map((player, index) => (
                      <li key={index} className="text-muted-foreground">• {player}</li>
                    )) || <li className="text-muted-foreground">No key players listed</li>}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Match Analysis */}
          <Card className="bg-card border-card-border shadow-card">
            <CardContent className="p-6 space-y-4">
              <h4 className="font-semibold text-foreground mb-4">Match Analysis</h4>
              
              <div className="space-y-4">
                <div>
                  <span className="font-semibold text-foreground">Team Analysis: </span>
                  <span className="text-muted-foreground">{matchData.prediction_object.supporting.team_analysis || "Data unavailable"}</span>
                </div>
                
                {matchData.prediction_object.supporting.h2h_summary && 
                 matchData.prediction_object.supporting.h2h_summary.toLowerCase() !== "data unavailable" && (
                  <div>
                    <span className="font-semibold text-foreground">H2H Summary: </span>
                    <span className="text-muted-foreground">{matchData.prediction_object.supporting.h2h_summary}</span>
                  </div>
                )}
                
                {matchData.prediction_object.supporting.recent_form_summary && 
                 matchData.prediction_object.supporting.recent_form_summary.toLowerCase() !== "data unavailable" && (
                  <div>
                    <span className="font-semibold text-foreground">Recent Form: </span>
                    <span className="text-muted-foreground">{matchData.prediction_object.supporting.recent_form_summary}</span>
                  </div>
                )}

                {matchData.prediction_object.supporting.venue_analysis && 
                 matchData.prediction_object.supporting.venue_analysis !== "data unavailable" && (
                  <div>
                    <span className="font-semibold text-foreground">Venue Analysis: </span>
                    <span className="text-muted-foreground">{matchData.prediction_object.supporting.venue_analysis}</span>
                  </div>
                )}

                {matchData.prediction_object.supporting.momentum_factors && 
                 matchData.prediction_object.supporting.momentum_factors !== "data unavailable" && (
                  <div>
                    <span className="font-semibold text-foreground">Momentum Factors: </span>
                    <span className="text-muted-foreground">{matchData.prediction_object.supporting.momentum_factors}</span>
                  </div>
                )}

                {matchData.prediction_object.supporting.tactical_insights && 
                 matchData.prediction_object.supporting.tactical_insights !== "data unavailable" && (
                  <div>
                    <span className="font-semibold text-foreground">Tactical Insights: </span>
                    <span className="text-muted-foreground">{matchData.prediction_object.supporting.tactical_insights}</span>
                  </div>
                )}

                {matchData.prediction_object.supporting.key_player_matchups && 
                 matchData.prediction_object.supporting.key_player_matchups.toLowerCase() !== "data unavailable" && (
                  <div>
                    <span className="font-semibold text-foreground">Key Player Matchups: </span>
                    <span className="text-muted-foreground">{matchData.prediction_object.supporting.key_player_matchups}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Match Conditions - Only show if any data is available */}
          {((matchData.prediction_object.supporting.pitch_conditions && 
             matchData.prediction_object.supporting.pitch_conditions !== "Data unavailable") ||
            (matchData.prediction_object.supporting.weather_conditions && 
             matchData.prediction_object.supporting.weather_conditions !== "Data unavailable") ||
            (matchData.prediction_object.supporting.injury_reports && 
             matchData.prediction_object.supporting.injury_reports !== "Data unavailable") ||
            (matchData.venue)) && (
            <Card className="bg-card border-card-border shadow-card">
              <CardContent className="p-6 space-y-4">
                <h4 className="font-semibold text-foreground mb-4">Match Conditions & Data Quality</h4>
                
                <div className="space-y-3">
                  {matchData.venue && (
                    <div>
                      <span className="font-semibold text-foreground">Venue: </span>
                      <span className="text-muted-foreground">{matchData.venue}</span>
                    </div>
                  )}
                  {matchData.prediction_object.supporting.pitch_conditions && 
                   matchData.prediction_object.supporting.pitch_conditions.toLowerCase() !== "data unavailable" && (
                    <div>
                      <span className="font-semibold text-foreground">Pitch Conditions: </span>
                      <span className="text-muted-foreground">{matchData.prediction_object.supporting.pitch_conditions}</span>
                    </div>
                  )}

                  {matchData.prediction_object.supporting.weather_conditions && 
                   matchData.prediction_object.supporting.weather_conditions.toLowerCase() !== "data unavailable" && (
                    <div>
                      <span className="font-semibold text-foreground">Weather: </span>
                      <span className="text-muted-foreground">{matchData.prediction_object.supporting.weather_conditions}</span>
                    </div>
                  )}

                  {matchData.prediction_object.supporting.injury_reports && 
                   matchData.prediction_object.supporting.injury_reports.toLowerCase() !== "data unavailable" && (
                    <div>
                      <span className="font-semibold text-foreground">Injury Reports: </span>
                      <span className="text-muted-foreground">{matchData.prediction_object.supporting.injury_reports}</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Betting Information */}
          <Card className="bg-card border-card-border shadow-card">
            <CardContent className="p-6">
              <h4 className="font-semibold text-foreground mb-4">Betting Information</h4>
              
              {/* Match Odds */}
              <div className="mb-6">
                <h5 className="font-semibold text-foreground mb-3">Bookmaker Odds:</h5>
                <div className="space-y-2">
                  <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                    <span className="text-sm text-foreground">{matchData.prediction_object.teams.a_name}</span>
                    <span className="text-sm font-bold text-black bg-brand-primary px-2 py-1 rounded">
                      {matchData.prediction_object.bookmaker_odds.team_a_odds}
                    </span>
                  </div>
                  <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                    <span className="text-sm text-foreground">{matchData.prediction_object.teams.b_name}</span>
                    <span className="text-sm font-bold text-black bg-brand-primary px-2 py-1 rounded">
                      {matchData.prediction_object.bookmaker_odds.team_b_odds}
                    </span>
                  </div>
                </div>
              </div>

              {/* Match Probabilities */}
              <div className="mb-6">
                <h5 className="font-semibold text-foreground mb-3">Win Probabilities:</h5>
                <div className="space-y-3">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-foreground">{matchData.prediction_object.teams.a_name}</span>
                      <span className="text-sm font-semibold text-foreground">
                        {matchData.prediction_object.prediction.a_win_pct}%
                      </span>
                    </div>
                    <div className="w-full bg-surface rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${matchData.prediction_object.prediction.a_win_pct > 50 ? 'bg-brand-primary' : 'bg-red-500'}`}
                        style={{ width: `${matchData.prediction_object.prediction.a_win_pct}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-foreground">{matchData.prediction_object.teams.b_name}</span>
                      <span className="text-sm font-semibold text-foreground">
                        {matchData.prediction_object.prediction.b_win_pct}%
                      </span>
                    </div>
                    <div className="w-full bg-surface rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${matchData.prediction_object.prediction.b_win_pct > 50 ? 'bg-brand-primary' : 'bg-red-500'}`}
                        style={{ width: `${matchData.prediction_object.prediction.b_win_pct}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Betting Recommendation */}
              {matchData.prediction_object.betting_recommendation && (
                <div className="bg-surface rounded-lg p-4">
                  <h5 className="font-semibold text-foreground mb-2">Betting Recommendation:</h5>
                  <p className="text-muted-foreground text-sm">{matchData.prediction_object.betting_recommendation}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Risk Factors & Explanation */}
          <Card className="bg-card border-card-border shadow-card">
            <CardContent className="p-6 space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-foreground">EXPLANATION:</h4>
                  {matchData.summary && 
                   matchData.summary.toLowerCase() !== "data unavailable" && (
                     <Dialog>
                       <DialogTrigger asChild>
                         <Button variant="ghost" size="sm" className="h-6 w-6 p-0 hover:bg-surface">
                           <Eye className="h-4 w-4 text-muted-foreground" />
                         </Button>
                       </DialogTrigger>
                       <DialogContent className="max-w-2xl bg-card border-card-border">
                         <DialogHeader>
                           <DialogTitle className="text-foreground">MATCH SUMMARY</DialogTitle>
                         </DialogHeader>
                         <div className="mt-4">
                           <p className="text-sm text-muted-foreground leading-relaxed">{matchData.summary}</p>
                         </div>
                       </DialogContent>
                     </Dialog>
                   )}
                </div>
                <p className="text-muted-foreground">{matchData.explanation}</p>
              </div>

              {matchData.prediction_object.supporting.summary && 
               matchData.prediction_object.supporting.summary.toLowerCase() !== "data unavailable" && (
                <div>
                  <h4 className="font-semibold text-foreground mb-2">Summary:</h4>
                  <p className="text-muted-foreground">{matchData.prediction_object.supporting.summary}</p>
                </div>
              )}

              {matchData.prediction_object.risk_factors && (
                <div>
                  <h4 className="font-semibold text-foreground mb-2">Risk Factors:</h4>
                  <p className="text-muted-foreground">{matchData.prediction_object.risk_factors}</p>
                </div>
              )}

              {/* Match Start */}
              <div className="pt-4 border-t border-border">
                <p className="text-sm text-muted-foreground">
                  <span className="font-semibold">MATCH START:</span> {formatMatchTime(matchData.match_kick_off)}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default CricketDetails;