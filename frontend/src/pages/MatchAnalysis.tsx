import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft } from "lucide-react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useNavigate, useParams } from "react-router-dom";
import { useState, useEffect } from "react";

const MatchAnalysis = () => {
  const navigate = useNavigate();
  const { matchId } = useParams();
  const [matchData, setMatchData] = useState<any>(null);

  useEffect(() => {
    if (matchId) {
      // Load match data from localStorage
      const storedData = localStorage.getItem(`match_analysis_${matchId}`);
      if (storedData) {
        const prediction = JSON.parse(storedData);
        setMatchData(prediction);
      }
    }
  }, [matchId]);

  if (!matchData) {
    return (
      <DashboardLayout>
        <div className="min-h-screen bg-background p-6">
          <div className="max-w-4xl mx-auto space-y-6">
            <Button 
              variant="outline" 
              onClick={() => navigate('/football-predictions')}
              className="flex items-center gap-2 border-border text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Predictions
            </Button>
            <Card className="bg-card border-card-border shadow-card">
              <CardContent className="p-6 text-center">
                <p className="text-muted-foreground">Match data not found. Please go back and select a match.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const predictionData = matchData.prediction_object;
  const teams = predictionData.teams;
  const homeTeam = teams.home;
  const awayTeam = teams.away;

  const getProgressColor = (probability: number) => {
    if (probability > 50) return "bg-brand-primary";
    if (probability > 30) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Back Button */}
          <Button 
            variant="outline" 
            onClick={() => navigate('/football-predictions')}
            className="flex items-center gap-2 border-border text-muted-foreground hover:text-black"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Predictions
          </Button>

          {/* Match Header Card */}
          <Card className="bg-card border-card-border shadow-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-center space-x-8">
                <div className="text-center">
                  <div className="w-16 h-16 bg-surface rounded-full flex items-center justify-center mx-auto mb-2 overflow-hidden border border-border">
                    {matchData.logos?.team_a ? (
                      <img 
                        src={matchData.logos.team_a} 
                        alt={`${homeTeam} logo`}
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          const target = e.currentTarget;
                          target.style.display = 'none';
                          const parent = target.parentElement;
                          if (parent) {
                            parent.innerHTML = `<span class="text-foreground font-bold text-xs">${homeTeam.substring(0, 3).toUpperCase()}</span>`;
                          }
                        }}
                      />
                    ) : (
                      <span className="text-foreground font-bold text-xs">{homeTeam.substring(0, 3).toUpperCase()}</span>
                    )}
                  </div>
                  <p className="font-semibold text-foreground">{homeTeam}</p>
                </div>
                
                <div className="text-center">
                  <span className="text-2xl font-bold text-muted-foreground">VS</span>
                </div>
                
                <div className="text-center">
                  <div className="w-16 h-16 bg-surface rounded-full flex items-center justify-center mx-auto mb-2 overflow-hidden border border-border">
                    {matchData.logos?.team_b ? (
                      <img 
                        src={matchData.logos.team_b} 
                        alt={`${awayTeam} logo`}
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          const target = e.currentTarget;
                          target.style.display = 'none';
                          const parent = target.parentElement;
                          if (parent) {
                            parent.innerHTML = `<span class="text-foreground font-bold text-xs">${awayTeam.substring(0, 3).toUpperCase()}</span>`;
                          }
                        }}
                      />
                    ) : (
                      <span className="text-foreground font-bold text-xs">{awayTeam.substring(0, 3).toUpperCase()}</span>
                    )}
                  </div>
                  <p className="font-semibold text-foreground">{awayTeam}</p>
                </div>
              </div>
              
              <div className="text-center mt-6 space-y-2">
                <h3 className="text-lg font-semibold text-muted-foreground">Prediction</h3>
                <p className="text-xl font-bold text-brand-accent">{matchData.predicted_winner} TO WIN</p>
                <div className="w-full bg-surface rounded-full h-2 mt-2">
                  <div 
                    className="bg-brand-primary h-2 rounded-full" 
                    style={{ width: `${matchData.win_probability_percent}%` }}
                  ></div>
                </div>
                <p className="text-sm text-muted-foreground">Win Probability: {matchData.win_probability_percent}%</p>
              </div>
            </CardContent>
          </Card>

          {/* Match Details */}
          <Card className="bg-card border-card-border shadow-card">
            <CardContent className="p-6 space-y-4">
              <h3 className="text-lg font-semibold text-foreground">MATCH: {matchData.match_name}</h3>
              
              <div>
                <h4 className="font-semibold text-foreground mb-2">EXPLANATION:</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">{predictionData.explanation}</p>
              </div>

              {/* Match Explanation */}
              {predictionData.match_explanation && (
                <div>
                  <h4 className="font-semibold text-foreground mb-2">DETAILED ANALYSIS:</h4>
                  <p className="text-sm text-muted-foreground leading-relaxed">{predictionData.match_explanation}</p>
                </div>
              )}

              {/* Win Probabilities */}
              <div>
                <h4 className="font-semibold text-foreground mb-3">Win Probabilities:</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{homeTeam} Win</span>
                    <div className="flex items-center gap-3 flex-1 ml-4">
                      <div className="flex-1 bg-surface rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${getProgressColor(predictionData.probabilitiesr.home)}`}
                          style={{ width: `${predictionData.probabilitiesr.home}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold text-foreground w-12 text-right">
                        {predictionData.probabilitiesr.home}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Draw</span>
                    <div className="flex items-center gap-3 flex-1 ml-4">
                      <div className="flex-1 bg-surface rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${getProgressColor(predictionData.probabilitiesr.draw)}`}
                          style={{ width: `${predictionData.probabilitiesr.draw}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold text-foreground w-12 text-right">
                        {predictionData.probabilitiesr.draw}%
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{awayTeam} Win</span>
                    <div className="flex items-center gap-3 flex-1 ml-4">
                      <div className="flex-1 bg-surface rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${getProgressColor(predictionData.probabilitiesr.away)}`}
                          style={{ width: `${predictionData.probabilitiesr.away}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-semibold text-foreground w-12 text-right">
                        {predictionData.probabilitiesr.away}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Expected Goals */}
              <div>
                <h4 className="font-semibold text-foreground mb-3">Expected Goals (xG):</h4>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(predictionData.xg_estimates).map(([team, data]: [string, any]) => (
                    <div key={team} className="flex items-center justify-between bg-surface rounded-lg p-3">
                      <span className="text-sm text-foreground">{team}</span>
                      <span className="text-lg font-bold text-brand-accent">{data.xg}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Match Odds */}
              <div>
                <h4 className="font-semibold text-foreground mb-3">Match Odds:</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                    <span className="text-sm text-foreground">{homeTeam}</span>
                    <span className="text-sm font-bold text-brand-accent">{predictionData.match_odds.home}</span>
                  </div>
                  <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                    <span className="text-sm text-foreground">Draw</span>
                    <span className="text-sm font-bold text-brand-accent">{predictionData.match_odds.draw}</span>
                  </div>
                  <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                    <span className="text-sm text-foreground">{awayTeam}</span>
                    <span className="text-sm font-bold text-brand-accent">{predictionData.match_odds.away}</span>
                  </div>
                </div>
              </div>

              {/* Fair Odds */}
              <div>
                <h4 className="font-semibold text-foreground mb-3">Fair Odds:</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                    <span className="text-sm text-foreground">{homeTeam}</span>
                    <span className="text-sm font-bold text-brand-accent">{predictionData.fair_odds.home}</span>
                  </div>
                  <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                    <span className="text-sm text-foreground">Draw</span>
                    <span className="text-sm font-bold text-brand-accent">{predictionData.fair_odds.draw}</span>
                  </div>
                  <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                    <span className="text-sm text-foreground">{awayTeam}</span>
                    <span className="text-sm font-bold text-brand-accent">{predictionData.fair_odds.away}</span>
                  </div>
                </div>
              </div>

              {/* Expected Value */}
              {predictionData.ev && (
                <div>
                  <h4 className="font-semibold text-foreground mb-3">Expected Value (EV):</h4>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                      <span className="text-sm text-foreground">{homeTeam}</span>
                      <span className="text-sm font-bold text-brand-accent">{predictionData.ev.home}%</span>
                    </div>
                    <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                      <span className="text-sm text-foreground">Draw</span>
                      <span className="text-sm font-bold text-brand-accent">{predictionData.ev.draw}%</span>
                    </div>
                    <div className="flex items-center justify-between bg-surface rounded-lg p-3">
                      <span className="text-sm text-foreground">{awayTeam}</span>
                      <span className="text-sm font-bold text-brand-accent">{predictionData.ev.away}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Confidence Level */}
              {predictionData.raw?.confidence_level && (
                <div>
                  <h4 className="font-semibold text-foreground mb-3">Confidence Level:</h4>
                  <div className="bg-surface rounded-lg p-3">
                    <span className="text-sm font-bold text-brand-accent">{predictionData.raw.confidence_level}</span>
                  </div>
                </div>
              )}

              {/* Kickoff Time */}
              <div className="pt-4 border-t border-border">
                <p className="text-sm text-muted-foreground">
                  <span className="font-semibold">KICKOFF TIME:</span> {new Date(matchData.match_kick_off).toLocaleString()}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default MatchAnalysis;