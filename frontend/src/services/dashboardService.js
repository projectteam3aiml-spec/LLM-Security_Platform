import api from './api';

export const dashboardService = {
  getStats: async () => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  getRiskDistribution: async () => {
    const response = await api.get('/dashboard/risk-distribution');
    return response.data;
  },

  getThreatTrends: async (hours = 24) => {
    const response = await api.get('/dashboard/threat-trends', { params: { hours } });
    return response.data;
  },

  getModelHealth: async () => {
    const response = await api.get('/dashboard/model-health');
    return response.data;
  }
};
