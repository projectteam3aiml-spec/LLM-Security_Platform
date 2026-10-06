import api from './api';

export const policyService = {
  // Trailing slash matches the backend route exactly (policies.router's "/"
  // under the "/policies" prefix) -- omitting it works too via FastAPI's
  // redirect_slashes, but that 307 round trip is an avoidable extra hop
  // cross-origin, so we just call the real path directly.
  getPolicies: async () => {
    const response = await api.get('/policies/');
    return response.data;
  },

  // Bulk upsert: backend expects { policies: [...] } (see PolicyUpdateRequest
  // in app/schemas/policy.py), not a bare array.
  updatePolicies: async (policies) => {
    const response = await api.put('/policies/', { policies });
    return response.data;
  }
};
