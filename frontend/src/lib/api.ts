import axios from 'axios';

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  'http://127.0.0.1:8000/api/v1';
const AUTH_TOKEN_KEY = 'jwt_token';
const USER_ROLE_KEY = 'user_role';
const NGO_ID_KEY = 'ngo_id';
const USER_NAME_KEY = 'user_name';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Axios Interceptor to automatically attach Bearer token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Optional: Response interceptor for handling 401s
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearAuthStorage();
    }
    return Promise.reject(error);
  }
);

export function clearAuthStorage() {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(USER_ROLE_KEY);
  localStorage.removeItem(NGO_ID_KEY);
  localStorage.removeItem(USER_NAME_KEY);
}

export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function getUserRole() {
  return localStorage.getItem(USER_ROLE_KEY);
}

export function setUserSession(profile: any, token?: string) {
  if (token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  }
  if (profile?.role) {
    localStorage.setItem(USER_ROLE_KEY, profile.role);
  }
  if (profile?.ngo_id) {
    localStorage.setItem(NGO_ID_KEY, String(profile.ngo_id));
  } else {
    localStorage.removeItem(NGO_ID_KEY);
  }
  if (profile?.name) {
    localStorage.setItem(USER_NAME_KEY, profile.name);
  }
}

export const api = {
  // --- AUTH ---
  register: (data: any) => apiClient.post('/auth/register', data).then(res => res.data),
  registerNgo: (data: any) => apiClient.post('/auth/register-ngo', data).then(res => res.data),
  login: (data: any) => apiClient.post('/auth/login', data).then(res => res.data),
  getProfile: () => apiClient.get('/auth/me').then(res => res.data),
  logout: () => apiClient.post('/auth/logout').then(res => res.data),
  changePassword: (data: any) => apiClient.post('/auth/change-password', data).then(res => res.data),

  // --- NGOS ---
  createNgo: (data: any) => apiClient.post('/ngos', data).then(res => res.data),
  getNgos: () => apiClient.get('/ngos').then(res => res.data),
  getNgo: (id: string) => apiClient.get(`/ngos/${id}`).then(res => res.data),
  verifyNgo: (id: string, data: any) => apiClient.patch(`/ngos/${id}/verify`, data).then(res => res.data),
  addNgoMember: (id: string, data: any) => apiClient.post(`/ngos/${id}/members`, data).then(res => res.data),
  addNgoMemberByEmail: (id: string, data: any) => apiClient.post(`/ngos/${id}/members/by-email`, data).then(res => res.data),
  getNgoMembers: (id: string) => apiClient.get(`/ngos/${id}/members`).then(res => res.data),

  // --- LOCATIONS ---
  geocode: (data: any) => apiClient.post('/locations/geocode', data).then(res => res.data),
  reverseGeocode: (data: any) => apiClient.post('/locations/reverse', data).then(res => res.data),

  // --- PROBLEMS ---
  createProblem: (data: any) => apiClient.post('/problems', data).then(res => res.data),
  getProblems: (filters = '') => apiClient.get(`/problems${filters}`).then(res => res.data),
  addProblemProof: (id: string, data: any) => apiClient.post(`/problems/${id}/proofs`, data).then(res => res.data),
  getProblem: (id: string) => apiClient.get(`/problems/${id}`).then(res => res.data),
  verifyProblem: (id: string, data: any) => apiClient.patch(`/problems/${id}/verify`, data).then(res => res.data),

  // --- TASKS ---
  createTask: (data: any) => apiClient.post('/tasks', data).then(res => res.data),
  getTasks: (filters = '') => apiClient.get(`/tasks${filters}`).then(res => res.data),
  assignTask: (id: string, data: any) => apiClient.post(`/tasks/${id}/assign`, data).then(res => res.data),
  acceptTask: (id: string) => apiClient.patch(`/tasks/${id}/accept`).then(res => res.data),
  addTaskProof: (id: string, data: any) => apiClient.post(`/tasks/${id}/proofs`, data).then(res => res.data),
  completeTask: (id: string) => apiClient.patch(`/tasks/${id}/complete`).then(res => res.data),

  // --- SKILLS & SURVEY ---
  addUserSkills: (data: any) => apiClient.post('/users/skills', data).then(res => res.data),
  getSkills: () => apiClient.get('/skills').then(res => res.data),
  submitSurvey: (data: any) => apiClient.post('/surveys', data).then(res => res.data),

  // --- RESOURCES ---
  getResourceTypes: () => apiClient.get('/resource-types').then(res => res.data),
  getInventory: () => apiClient.get('/resources/inventory').then(res => res.data),
  addInventory: (data: any) => apiClient.post('/resources/inventory', data).then(res => res.data),
  addTaskRequirement: (id: string, data: any) => apiClient.post(`/tasks/${id}/requirements`, data).then(res => res.data),
  allocateResource: (data: any) => apiClient.post('/resources/allocate', data).then(res => res.data),

  // --- FINANCE ---
  getDonations: () => apiClient.get('/donations').then(res => res.data),
  createDonation: (data: any) => apiClient.post('/donations', data).then(res => res.data),
  initiatePayment: (data: any) => apiClient.post('/payments/initiate', data).then(res => res.data),
  paymentWebhook: (data: any) => apiClient.post('/payments/webhook', data).then(res => res.data),
  getWallet: (ngoId: string) => apiClient.get(`/ngos/${ngoId}/wallet`).then(res => res.data),
  getLedger: (ngoId: string) => apiClient.get(`/ngos/${ngoId}/ledger`).then(res => res.data),

  // --- MISC / AI / NOTIFICATIONS / IMPORT ---
  getAiMatches: (problemId: string) => apiClient.get(`/ai/matches?problem_id=${problemId}`).then(res => res.data),
  getAiInsights: () => apiClient.get('/ai/insights').then(res => res.data),
  getNotifications: () => apiClient.get('/notifications').then(res => res.data),
  markNotificationRead: (id: string) => apiClient.patch(`/notifications/${id}/read`).then(res => res.data),
  importUpload: (data: any) => apiClient.post('/import/upload', data).then(res => res.data),
  importPreview: (id: string) => apiClient.get(`/import/${id}/preview`).then(res => res.data),
  importConfirm: (id: string) => apiClient.post(`/import/${id}/confirm`).then(res => res.data),

  // --- PUBLIC ---
  getPublicStats: () => apiClient.get('/public/stats').then(res => res.data),
  getPublicProblems: () => apiClient.get('/public/problems').then(res => res.data),
  publicJoin: (data: any) => apiClient.post('/public/join', data).then(res => res.data),
  publicVolunteerOptIn: () => apiClient.post('/public/volunteer-opt-in').then(res => res.data),
};
