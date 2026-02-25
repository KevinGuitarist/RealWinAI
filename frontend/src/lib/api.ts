import axios, { AxiosResponse, AxiosError } from 'axios';
import { config } from './config';
import { getAccessToken, isTokenExpired, clearAuthTokens, isAuthenticated } from './auth';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token && !isTokenExpired()) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token expiration
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle token expiration
    if (error.response?.status === 401 || error.response?.status === 403) {
      clearAuthTokens();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Check token validity periodically
const checkTokenValidity = () => {
  if (isAuthenticated() && isTokenExpired()) {
    clearAuthTokens();
    window.location.href = '/login';
  }
};

// Check token every 5 minutes
setInterval(checkTokenValidity, 5 * 60 * 1000);

// Subscription API functions
export async function startSubscription(payload: { email: string; full_name: string }) {
  const response = await api.post('/subscriptions/start', payload);
  return response.data as { subscriptionId: number; orderId: string; token: string; checkout_url: string };
}

export async function getMySubscription() {
  const response = await api.get('/subscriptions/me');
  return response.data as {
    id: number;
    email: string;
    full_name?: string;
    status: string;
    is_active: boolean;
    next_billing_at?: string;
  };
}

export async function cancelMySubscription() {
  const response = await api.post('/subscriptions/cancel');
  return response.data;
}

// Admin API functions
export async function getUsersSubscriptions(params?: {
  limit?: number;
  offset?: number;
  status?: string;
  email?: string;
  order_by?: string;
  order_dir?: string;
}) {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());
  if (params?.status) queryParams.append('status', params.status);
  if (params?.email) queryParams.append('email', params.email);
  if (params?.order_by) queryParams.append('order_by', params.order_by);
  if (params?.order_dir) queryParams.append('order_dir', params.order_dir);
  
  const response = await api.get(`/admin/users-subscriptions?${queryParams.toString()}`);
  return response.data;
}

export async function getJobs(params?: {
  limit?: number;
  offset?: number;
  order_by?: string;
  order_dir?: string;
}) {
  const queryParams = new URLSearchParams();
  if (params?.limit) queryParams.append('limit', params.limit.toString());
  if (params?.offset) queryParams.append('offset', params.offset.toString());
  if (params?.order_by) queryParams.append('order_by', params.order_by);
  if (params?.order_dir) queryParams.append('order_dir', params.order_dir);
  
  const response = await api.get(`/admin/jobs?${queryParams.toString()}`);
  return response.data;
}

// Football Predictions API
export async function getFootballPredictions(date: string) {
  const response = await api.get(`/predictions/football?date=${date}`);
  return response.data;
}

// Cricket Predictions API
export async function getCricketPredictions(date: string) {
  const response = await api.get(`/predictions/cricket?date=${date}`);
  return response.data;
}

// ========================================
// MAX ENHANCED FEATURES API
// ========================================

// Track Record API
export async function getTrackRecord(params?: {
  sport?: string;
  days?: number;
}) {
  const queryParams = new URLSearchParams();
  if (params?.sport) queryParams.append('sport', params.sport);
  if (params?.days) queryParams.append('days', params.days.toString());
  
  const response = await api.get(`/max/enhanced/track-record?${queryParams.toString()}`);
  return response.data;
}

export async function verifyPrediction(predictionId: string) {
  const response = await api.post(`/max/enhanced/track-record/verify/${predictionId}`);
  return response.data;
}

// Explainable Predictions API
export async function explainPrediction(payload: {
  match_data: any;
  analysis_data: any;
}) {
  const response = await api.post('/max/enhanced/explain-prediction', payload, {
    timeout: 30000, // 30 seconds for AI processing
  });
  return response.data;
}

// Personalized Strategy API
export async function createStrategy(userId: number, payload: {
  bankroll: number;
  goals: {
    target_monthly_profit?: number;
    acceptable_drawdown?: number;
    time_horizon?: string;
  };
  risk_profile: string;
  preferences?: any;
}) {
  const response = await api.post(`/max/enhanced/strategy/create/${userId}`, payload);
  return response.data;
}

export async function getStrategyRecommendation(userId: number, params: {
  prediction: any;
  current_bankroll: number;
}) {
  const queryParams = new URLSearchParams({
    prediction: JSON.stringify(params.prediction),
    current_bankroll: params.current_bankroll.toString(),
  });
  
  const response = await api.get(
    `/max/enhanced/strategy/${userId}/recommendation?${queryParams.toString()}`
  );
  return response.data;
}

// Responsible Gambling API
export async function checkBettingSafety(userId: number, payload: {
  stake: number;
  odds: number;
  confidence?: number;
}) {
  const response = await api.post(`/max/enhanced/safety/check/${userId}`, payload);
  return response.data;
}

export async function setSpendingLimits(userId: number, limits: {
  daily_limit?: number;
  weekly_limit?: number;
  monthly_limit?: number;
}) {
  const response = await api.post(`/max/enhanced/safety/limits/${userId}`, limits);
  return response.data;
}

export async function getSpendingLimits(userId: number) {
  const response = await api.get(`/max/enhanced/safety/limits/${userId}`);
  return response.data;
}

export async function requestSelfExclusion(userId: number, payload: {
  duration_days: number;
  reason?: string;
}) {
  const response = await api.post(`/max/enhanced/safety/self-exclusion/${userId}`, payload);
  return response.data;
}

export async function getRealityCheck(userId: number) {
  const response = await api.get(`/max/enhanced/safety/reality-check/${userId}`);
  return response.data;
}

// Analytics Dashboard API
export async function getUserAnalytics(userId: number, timeframe: string = '30d') {
  const response = await api.get(
    `/max/enhanced/analytics/${userId}?timeframe=${timeframe}`
  );
  return response.data;
}

// Ensemble Predictions API
export async function getEnsemblePrediction(payload: {
  match_data: any;
  analysis_data: any;
}) {
  const response = await api.post('/max/enhanced/ensemble/predict', payload, {
    timeout: 45000, // 45 seconds for multi-model processing
  });
  return response.data;
}

export default api;