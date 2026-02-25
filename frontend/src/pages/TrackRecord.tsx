import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { getTrackRecord } from "@/lib/api";
import { TrendingUp, TrendingDown, Target, Award, Activity, Calendar } from "lucide-react";

const TrackRecord = () => {
  const [selectedSport, setSelectedSport] = useState<string>("all");
  const [timeframe, setTimeframe] = useState<number>(30);

  const { data, isLoading, error } = useQuery({
    queryKey: ['trackRecord', selectedSport, timeframe],
    queryFn: () => getTrackRecord({ 
      sport: selectedSport === "all" ? undefined : selectedSport,
      days: timeframe 
    }),
    refetchInterval: 60000, // Refetch every minute
  });

  const trackRecord = data?.data || {};
  const predictions = data?.predictions || [];

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-3 sm:p-6">
        <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Award className="w-6 h-6 sm:w-8 sm:h-8 text-brand-accent" />
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">MAX's Track Record</h1>
            </div>
            <p className="text-sm sm:text-base text-muted-foreground">
              Transparent, verified prediction history and performance metrics
            </p>
          </div>

          {/* Timeframe & Sport Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <Tabs value={timeframe.toString()} onValueChange={(v) => setTimeframe(Number(v))} className="flex-1">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="7">7 Days</TabsTrigger>
                <TabsTrigger value="30">30 Days</TabsTrigger>
                <TabsTrigger value="90">90 Days</TabsTrigger>
                <TabsTrigger value="365">1 Year</TabsTrigger>
              </TabsList>
            </Tabs>

            <Tabs value={selectedSport} onValueChange={setSelectedSport}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="all">All Sports</TabsTrigger>
                <TabsTrigger value="cricket">Cricket</TabsTrigger>
                <TabsTrigger value="football">Football</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Activity className="w-8 h-8 animate-spin text-brand-accent" />
            </div>
          ) : error ? (
            <Card className="bg-destructive/10 border-destructive">
              <CardContent className="p-6">
                <p className="text-destructive">Failed to load track record. Please try again.</p>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Key Metrics */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      Total Predictions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-foreground">
                      {trackRecord.total_predictions || 0}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {trackRecord.verified_predictions || 0} verified
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" />
                      Accuracy
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-foreground">
                      {trackRecord.accuracy_percentage || 0}%
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Win rate on verified predictions
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      ROI
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-3xl font-bold ${
                      (trackRecord.roi_percentage || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      {trackRecord.roi_percentage > 0 ? '+' : ''}{trackRecord.roi_percentage || 0}%
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Return on investment
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      {(trackRecord.total_profit_loss || 0) >= 0 ? (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      Profit/Loss
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-3xl font-bold ${
                      (trackRecord.total_profit_loss || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      £{Math.abs(trackRecord.total_profit_loss || 0).toFixed(2)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Based on £10 unit stakes
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Confidence Calibration */}
              {trackRecord.confidence_calibration && (
                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader>
                    <CardTitle className="text-lg">Confidence Calibration</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      How well MAX's confidence matches actual outcomes
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 sm:grid-cols-3">
                      {Object.entries(trackRecord.confidence_calibration).map(([range, data]: [string, any]) => (
                        <div key={range} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">{range}</span>
                            <Badge variant={data.actual_win_rate >= 50 ? "default" : "secondary"}>
                              {data.actual_win_rate}% actual
                            </Badge>
                          </div>
                          <div className="w-full bg-surface rounded-full h-2">
                            <div 
                              className="bg-brand-primary h-2 rounded-full transition-all"
                              style={{ width: `${data.actual_win_rate}%` }}
                            />
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {data.count} predictions
                          </p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Recent Predictions */}
              <Card className="bg-card border-card-border shadow-card">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Recent Predictions
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {predictions.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      No predictions in this timeframe
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {predictions.slice(0, 10).map((pred: any, index: number) => (
                        <div 
                          key={index}
                          className="flex items-center justify-between p-4 bg-surface rounded-lg"
                        >
                          <div className="flex-1">
                            <p className="font-medium text-foreground">{pred.match_description}</p>
                            <p className="text-sm text-muted-foreground">{pred.prediction_type}</p>
                          </div>
                          <div className="flex items-center gap-4">
                            <Badge 
                              variant={pred.confidence >= 70 ? "default" : "secondary"}
                              className="min-w-[60px] justify-center"
                            >
                              {pred.confidence}% conf
                            </Badge>
                            {pred.outcome && (
                              <Badge 
                                variant={pred.outcome === 'won' ? "default" : "destructive"}
                                className="min-w-[60px] justify-center"
                              >
                                {pred.outcome === 'won' ? '✓ Won' : '✗ Lost'}
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Disclaimer */}
              <Card className="bg-surface border-border">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground text-center">
                    All predictions are verified independently. Past performance does not guarantee future results. 
                    Bet responsibly and within your means.
                  </p>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default TrackRecord;
