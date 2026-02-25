import { useState, useEffect } from 'react';
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Calendar, Filter, RefreshCw, TrendingUp, Eye } from "lucide-react";
import { getCricketPredictions, getFootballPredictions } from "@/lib/api";
import { toast } from "sonner";

interface Prediction {
  id?: string;
  match_name?: string;
  home_team?: string;
  away_team?: string;
  predicted_winner?: string;
  win_probability?: number;
  win_probability_percent?: number; // Football predictions use this field
  match_time?: string;
  match_kick_off?: string; // Football predictions use this field
  confidence_level?: string;
  key_insights?: string[];
}

const AdminPredictions = () => {
  const [cricketPredictions, setCricketPredictions] = useState<Prediction[]>([]);
  const [footballPredictions, setFootballPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("cricket");
  const [confidenceFilter, setConfidenceFilter] = useState("all");
  const [probabilityFilter, setProbabilityFilter] = useState("all");
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchPredictions = async () => {
    setLoading(true);
    try {
      const [cricketData, footballData] = await Promise.all([
        getCricketPredictions(selectedDate),
        getFootballPredictions(selectedDate)
      ]);
      
      console.log('Cricket data:', cricketData);
      console.log('Football data:', footballData);
      
      setCricketPredictions(Array.isArray(cricketData) ? cricketData : cricketData?.predictions || []);
      setFootballPredictions(Array.isArray(footballData) ? footballData : footballData?.predictions || []);
    } catch (error) {
      console.error('Error fetching predictions:', error);
      toast.error('Failed to fetch predictions');
      // Set sample data for testing
      setCricketPredictions([
        {
          id: '1',
          match_name: 'India vs Australia',
          predicted_winner: 'India',
          win_probability: 75.5,
          match_time: '2024-01-15T14:30:00Z',
          confidence_level: 'high'
        },
        {
          id: '2',
          match_name: 'England vs Pakistan',
          predicted_winner: 'England',
          win_probability: 82.3,
          match_time: '2024-01-16T10:00:00Z',
          confidence_level: 'high'
        }
      ]);
      setFootballPredictions([
        {
          id: '1',
          match_name: 'Manchester United vs Liverpool',
          predicted_winner: 'Manchester United',
          win_probability_percent: 68.2,
          match_kick_off: '2024-01-15T16:00:00Z',
          confidence_level: 'medium'
        },
        {
          id: '2',
          match_name: 'Arsenal vs Chelsea',
          predicted_winner: 'Arsenal',
          win_probability_percent: 71.8,
          match_kick_off: '2024-01-16T18:30:00Z',
          confidence_level: 'medium'
        },
        {
          id: '3',
          match_name: 'Manchester City vs Tottenham',
          predicted_winner: 'Manchester City',
          win_probability_percent: 85.1,
          match_kick_off: '2024-01-17T20:00:00Z',
          confidence_level: 'high'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictions();
  }, [selectedDate]);

  const getConfidenceLevel = (probability: number): string => {
    if (probability >= 80) return "high";
    if (probability >= 60) return "medium";
    return "low";
  };

  const getConfidenceBadgeVariant = (level: string) => {
    switch (level) {
      case "high": return "default";
      case "medium": return "secondary";
      case "low": return "outline";
      default: return "outline";
    }
  };

  const filterPredictions = (predictions: Prediction[]) => {
    return predictions.filter(prediction => {
      const probability = prediction.win_probability_percent || prediction.win_probability || 0;
      const confidence = prediction.confidence_level || getConfidenceLevel(probability);
      
      const matchesConfidence = confidenceFilter === "all" || confidence === confidenceFilter;
      
      const matchesProbability = 
        probabilityFilter === "all" ||
        (probabilityFilter === "high" && probability >= 80) ||
        (probabilityFilter === "medium" && probability >= 60 && probability < 80) ||
        (probabilityFilter === "low" && probability < 60);

      return matchesConfidence && matchesProbability;
    });
  };

  const currentPredictions = activeTab === "cricket" ? cricketPredictions : footballPredictions;
  const filteredPredictions = filterPredictions(currentPredictions);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-foreground">Admin Predictions Management</h1>
          <p className="text-muted-foreground">
            Manage and filter sports predictions with advanced controls
          </p>
        </div>

        {/* Filters */}
        <Card className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Date Filter */}
            <div>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-white ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
                style={{
                  colorScheme: 'dark'
                }}
              />
            </div>

            {/* Confidence Filter */}
            <Select value={confidenceFilter} onValueChange={setConfidenceFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Confidence Level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Confidence</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>

            {/* Probability Filter */}
            <Select value={probabilityFilter} onValueChange={setProbabilityFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Win Probability" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Probabilities</SelectItem>
                <SelectItem value="high">High (80%+)</SelectItem>
                <SelectItem value="medium">Medium (60-79%)</SelectItem>
                <SelectItem value="low">Low (&lt;60%)</SelectItem>
              </SelectContent>
            </Select>

            {/* Refresh Button */}
            <Button onClick={fetchPredictions} disabled={loading} variant="outline">
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </Card>

        {/* Predictions Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="cricket">Cricket Predictions</TabsTrigger>
            <TabsTrigger value="football">Football Predictions</TabsTrigger>
          </TabsList>

          <TabsContent value="cricket" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Cricket Predictions</h2>
              <Badge variant="secondary">{filteredPredictions.length} predictions</Badge>
            </div>
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} className="p-6 space-y-4">
                    <div className="animate-pulse space-y-3">
                      <div className="h-4 bg-muted rounded w-3/4"></div>
                      <div className="h-3 bg-muted rounded w-1/2"></div>
                      <div className="h-3 bg-muted rounded w-full"></div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : filteredPredictions.length > 0 ? (
              <div className="space-y-3">
                {filteredPredictions.map((prediction, index) => (
                  <PredictionRowCard key={index} prediction={prediction} sport="cricket" />
                ))}
              </div>
            ) : (
              <Card className="p-8 text-center">
                <p className="text-muted-foreground">No cricket predictions found for the selected filters.</p>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="football" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Football Predictions</h2>
              <Badge variant="secondary">{filteredPredictions.length} predictions</Badge>
            </div>
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} className="p-6 space-y-4">
                    <div className="animate-pulse space-y-3">
                      <div className="h-4 bg-muted rounded w-3/4"></div>
                      <div className="h-3 bg-muted rounded w-1/2"></div>
                      <div className="h-3 bg-muted rounded w-full"></div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : filteredPredictions.length > 0 ? (
              <div className="space-y-3">
                {filteredPredictions.map((prediction, index) => (
                  <PredictionRowCard key={index} prediction={prediction} sport="football" />
                ))}
              </div>
            ) : (
              <Card className="p-8 text-center">
                <p className="text-muted-foreground">No football predictions found for the selected filters.</p>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
};

interface PredictionRowCardProps {
  prediction: Prediction;
  sport: string;
}

const PredictionRowCard = ({ prediction, sport }: PredictionRowCardProps) => {
  const [showJson, setShowJson] = useState(false);
  
  // Handle different field names for different sports
  const probability = sport === "football" 
    ? (prediction.win_probability_percent || 0) 
    : (prediction.win_probability || 0);
    
  const matchTime = sport === "football" 
    ? prediction.match_kick_off 
    : prediction.match_time;

  const getConfidenceLevel = (probability: number): string => {
    if (probability >= 80) return "high";
    if (probability >= 60) return "medium";
    return "low";
  };

  const getConfidenceBadgeVariant = (level: string) => {
    switch (level) {
      case "high": return "default";
      case "medium": return "secondary";
      case "low": return "outline";
      default: return "outline";
    }
  };

  const formatMatchTime = (time: string | undefined) => {
    if (!time) return "Time TBD";
    try {
      const date = new Date(time);
      return date.toLocaleString();
    } catch {
      return time;
    }
  };

  const handleViewJson = () => {
    setShowJson(!showJson);
  };

  return (
    <Card className="p-4">
      <div className="space-y-4">
        {/* Match Name */}
        <div>
          <h3 className="font-semibold text-lg">
            {prediction.match_name || `${prediction.home_team} vs ${prediction.away_team}` || "Match TBD"}
          </h3>
          <p className="text-sm text-muted-foreground">
            Winner: {prediction.predicted_winner || "TBD"}
          </p>
        </div>

        {/* Match Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Kick Off Time */}
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              <span className="font-medium">Kick Off: </span>
              {formatMatchTime(matchTime)}
            </p>
          </div>

          {/* Win Probability */}
          <div className="space-y-2">
            <div className="text-sm text-muted-foreground">
              <span className="font-medium">Win Probability: </span>
              {probability.toFixed(1)}%
            </div>
            <Progress 
              value={probability} 
              className="w-full h-2"
            />
          </div>

          {/* Confidence Level */}
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground font-medium">Confidence Level:</p>
            <Badge variant={getConfidenceBadgeVariant(prediction.confidence_level || getConfidenceLevel(probability))}>
              {(prediction.confidence_level || getConfidenceLevel(probability)).toUpperCase()}
            </Badge>
          </div>
        </div>

        {/* View JSON Button */}
        <div className="flex justify-end pt-2 border-t border-border">
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleViewJson}
            className="flex items-center gap-2"
          >
            <Eye className="h-4 w-4" />
            {showJson ? "Hide JSON" : "View JSON"}
          </Button>
        </div>
      </div>

      {/* JSON Display */}
      {showJson && (
        <div className="mt-4 pt-4 border-t border-border">
          <div className="bg-muted p-4 rounded-lg">
            <h4 className="font-medium mb-2 text-sm">Full JSON Response:</h4>
            <pre className="text-xs overflow-x-auto whitespace-pre-wrap">
              {JSON.stringify(prediction, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </Card>
  );
};

export default AdminPredictions;