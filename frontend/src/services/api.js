import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', new URLSearchParams(credentials), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }),
  register: (data) => api.post('/api/auth/register', data),
  getMe: () => api.get('/api/auth/me'),
};

// Placement API
export const placementAPI = {
  analyze: (data) => api.post('/api/placement/analyze', data),
  getRecommendation: (filename, params) => api.get(`/api/placement/recommend/${filename}`, { params }),
  getRecommendations: () => api.get('/api/placement/recommendations'),
  getTierDistribution: () => api.get('/api/placement/tier-distribution'),
  analyzeBatch: (data) => api.post('/api/placement/analyze/batch', data),
  getTempClassification: () => api.get('/api/placement/temperature-classification'),
  getCostComparison: () => api.get('/api/placement/cost-comparison'),
};

// ML API
export const mlAPI = {
  getModelInfo: () => api.get('/api/ml/model-info'),
  getRecommendations: () => api.get('/api/ml/recommendations'),
  predictAccessPattern: (data) => api.post('/api/ml/predict/access-pattern', data),
  predictMigration: (data) => api.post('/api/ml/predict/migration', data),
  getInsightsSummary: () => api.get('/api/ml/insights/summary'),
};

// Migration API
export const migrationAPI = {
  getMigrations: () => api.get('/api/migration/jobs'),
  getMigration: (id) => api.get(`/api/migration/jobs/${id}`),
  createMigration: (data) => api.post('/api/migration/migrate', data),
  getStatus: () => api.get('/api/migration/status'),
};

// Streaming API
export const streamAPI = {
  getRecentEvents: (params) => api.get('/api/stream/events/recent', { params }),
  getStats: () => api.get('/api/stream/events/stats'),
  testEvent: (data) => api.post('/api/stream/events/test', data),
  getEventTypes: () => api.get('/api/stream/events/types'),
};

// Cloud Storage API
export const cloudStorageAPI = {
  getObjects: (provider) => api.get('/api/data/objects', { params: provider ? { provider, limit: 1000 } : { limit: 1000 } }),
  getObjectsByProvider: (provider) => api.get(`/api/data/objects/${provider}`),
};

// Analytics API
export const analyticsAPI = {
  getOverview: () => api.get('/api/analytics/overview'),
  getCosts: () => api.get('/api/analytics/costs'),
  getTiers: () => api.get('/api/data/tiers/distribution'),
};

// Security API
export const securityAPI = {
  getAuditLog: (hours = 24) => api.get('/api/security/audit-log', { params: { hours } }),
};

// General API
export const generalAPI = {
  getHealth: () => api.get('/health'),
  getCloudStatus: () => api.get('/api/cloud/status'),
  getDataObjects: (params) => api.get('/api/data/objects', { params }),
  getRoot: () => api.get('/'),
};

export default api;

