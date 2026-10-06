import api from './api';

export const analysisService = {
  analyzePrompt: async (promptData) => {
    const response = await api.post('/analyze', promptData);
    return response.data;
  },

  // Backs ThreatLogs.jsx / Overview.jsx's "recent events" table -- real
  // rows from the audit trail /analyze writes (see GET /api/v1/logs).
  getThreatLogs: async (limit = 50) => {
    const response = await api.get('/logs', { params: { limit } });
    return response.data;
  }
};