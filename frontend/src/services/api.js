import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      'An unexpected error occurred';
    return Promise.reject(new Error(message));
  }
);

export const fetchHealth = () => api.get('/api/health').then((r) => r.data);

export const fetchDatasetSummary = () =>
  api.get('/api/dataset/summary').then((r) => r.data);

export const fetchDatasetRecords = (params = {}) =>
  api.get('/api/dataset/records', { params }).then((r) => r.data);

export const fetchGradeDistribution = () =>
  api.get('/api/analytics/grades').then((r) => r.data);

export const fetchCorrelations = () =>
  api.get('/api/analytics/correlations').then((r) => r.data);

export const fetchInsights = () =>
  api.get('/api/analytics/insights').then((r) => r.data);

export const fetchFeatureImportance = () =>
  api.get('/api/analytics/feature-importance').then((r) => r.data);

export const fetchStatistics = () =>
  api.get('/api/analytics/statistics').then((r) => r.data);

export const fetchModelComparison = () =>
  api.get('/api/models/comparison').then((r) => r.data);

export const fetchModelMetadata = () =>
  api.get('/api/models/metadata').then((r) => r.data);

export const fetchErrorAnalysis = () =>
  api.get('/api/models/error-analysis').then((r) => r.data);

export const predictStudent = (data) =>
  api.post('/api/predict', data).then((r) => r.data);

export const predictBatch = (data) =>
  api.post('/api/predict/batch', data).then((r) => r.data);

export default api;
