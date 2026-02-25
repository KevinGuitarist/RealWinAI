import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { getUserAnalytics } from "@/lib/api";
import { getCurrentUser } from "@/lib/auth";
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Activity, 
  BarChart3,
  AlertTriangle,
  Award,
  Calendar
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

const Analytics = () => {
  const [timeframe, setTimeframe] = useState<string>('30d');
  const user = getCurrentUser();

  const { data, isLoading, error } = useQuery({
    queryKey: ['userAnalytics', user?.id, timeframe],
    queryFn: () => getUserAnalytics(user?.id || 0, timeframe),
    enabled: !!user?.id,
    refetchInterval: 60000, // Refetch every minute
  });

  const analytics = data?.data || {};
  const overview = analytics.overview || {};
  const trends = analytics.trends || [];
  const sportBreakdown = analytics.sport_breakdown || [];
  const marketBreakdown = analytics.market_breakdown || [];
  const insights = analytics.insights || [];
  const riskMetrics = analytics.risk_metrics || {};

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-background p-3 sm:p-6">
        <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-6 h-6 sm:w-8 sm:h-8 text-brand-accent" />
              <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Your Analytics</h1>
            </div>
            <p className="text-sm sm:text-base text-muted-foreground">
              Comprehensive performance insights and betting statistics
            </p>
          </div>

          {/* Timeframe Filter */}
          <Tabs value={timeframe} onValueChange={setTimeframe}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="7d">7 Days</TabsTrigger>
              <TabsTrigger value="30d">30 Days</TabsTrigger>
              <TabsTrigger value="90d">90 Days</TabsTrigger>
              <TabsTrigger value="1y">1 Year</TabsTrigger>
            </TabsList>
          </Tabs>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Activity className="w-8 h-8 animate-spin text-brand-accent" />
            </div>
          ) : error ? (
            <Card className="bg-destructive/10 border-destructive">
              <CardContent className="p-6">
                <p className="text-destructive">Failed to load analytics. Please try again.</p>
              </CardContent>
            </Card>
          ) : (
            <>
              {/* Key Metrics Overview */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      Win Rate
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-foreground">
                      {overview.win_rate || 0}%
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {overview.wins || 0}W - {overview.losses || 0}L
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
                      (overview.roi || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      {overview.roi > 0 ? '+' : ''}{overview.roi || 0}%
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Return on investment
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      {(overview.profit_loss || 0) >= 0 ? (
                        <TrendingUp className="w-4 h-4 text-green-500" />
                      ) : (
                        <TrendingDown className="w-4 h-4 text-red-500" />
                      )}
                      Profit/Loss
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`text-3xl font-bold ${
                      (overview.profit_loss || 0) >= 0 ? 'text-green-500' : 'text-red-500'
                    }`}>
                      £{Math.abs(overview.profit_loss || 0).toFixed(2)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Total P&L
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Total Bets
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold text-foreground">
                      {overview.total_bets || 0}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Avg stake: £{overview.avg_stake || 0}
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Performance Trend Chart */}
              {trends.length > 0 && (
                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader>
                    <CardTitle className="text-lg">Performance Trend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={trends}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis 
                          dataKey="date" 
                          stroke="#888"
                          fontSize={12}
                        />
                        <YAxis stroke="#888" fontSize={12} />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#1f1f1f', 
                            border: '1px solid #333',
                            borderRadius: '8px'
                          }}
                        />
                        <Legend />
                        <Line 
                          type="monotone" 
                          dataKey="cumulative_profit" 
                          stroke="#10b981" 
                          name="Cumulative Profit (£)"
                          strokeWidth={2}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="roi" 
                          stroke="#3b82f6" 
                          name="ROI (%)"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              )}

              {/* Sport & Market Breakdown */}
              <div className="grid gap-4 md:grid-cols-2">
                {/* Sport Breakdown */}
                {sportBreakdown.length > 0 && (
                  <Card className="bg-card border-card-border shadow-card">
                    <CardHeader>
                      <CardTitle className="text-lg">Performance by Sport</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                          <Pie
                            data={sportBreakdown}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ sport, profit_loss }) => `${sport}: £${profit_loss}`}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="profit_loss"
                          >
                            {sportBreakdown.map((entry: any, index: number) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1f1f1f', 
                              border: '1px solid #333',
                              borderRadius: '8px'
                            }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                )}

                {/* Market Breakdown */}
                {marketBreakdown.length > 0 && (
                  <Card className="bg-card border-card-border shadow-card">
                    <CardHeader>
                      <CardTitle className="text-lg">Performance by Market</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={marketBreakdown}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                          <XAxis 
                            dataKey="market" 
                            stroke="#888"
                            fontSize={11}
                            angle={-45}
                            textAnchor="end"
                            height={80}
                          />
                          <YAxis stroke="#888" fontSize={12} />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1f1f1f', 
                              border: '1px solid #333',
                              borderRadius: '8px'
                            }}
                          />
                          <Bar dataKey="win_rate" fill="#3b82f6" name="Win Rate (%)" />
                        </BarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Risk Metrics */}
              {Object.keys(riskMetrics).length > 0 && (
                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-yellow-500" />
                      Risk Metrics
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 sm:grid-cols-3">
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Max Drawdown</p>
                        <p className="text-2xl font-bold text-red-500">
                          {riskMetrics.max_drawdown || 0}%
                        </p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
                        <p className="text-2xl font-bold text-foreground">
                          {riskMetrics.sharpe_ratio || 0}
                        </p>
                      </div>
                      <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">Avg Win/Loss</p>
                        <p className="text-2xl font-bold text-foreground">
                          {riskMetrics.avg_win_loss_ratio || 0}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* AI Insights */}
              {insights.length > 0 && (
                <Card className="bg-card border-card-border shadow-card">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Award className="w-5 h-5 text-brand-accent" />
                      AI Insights & Recommendations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {insights.map((insight: string, index: number) => (
                        <div 
                          key={index}
                          className="flex items-start gap-3 p-3 bg-surface rounded-lg"
                        >
                          <Badge variant="outline" className="mt-0.5">
                            {index + 1}
                          </Badge>
                          <p className="text-sm text-foreground flex-1">{insight}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* No Data State */}
              {overview.total_bets === 0 && (
                <Card className="bg-surface border-border">
                  <CardContent className="p-8 text-center">
                    <Activity className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <h3 className="text-lg font-semibold text-foreground mb-2">
                      No Betting Data Yet
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Start placing bets to see your performance analytics and insights
                    </p>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Analytics;
