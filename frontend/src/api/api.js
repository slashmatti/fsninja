import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh and authentication errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/token/', data),
  refresh: (data) => api.post('/auth/refresh/', data),
};

// Sensors endpoints
export const sensorsAPI = {
  list: (params = {}) => api.get('/sensors/', { params }),
  create: (data) => api.post('/sensors/', data),
  get: (id) => api.get(`/sensors/${id}/`),
  update: (id, data) => api.put(`/sensors/${id}/`, data),
  delete: (id) => api.delete(`/sensors/${id}/`),
};

// Readings endpoints
export const readingsAPI = {
  list: (sensorId, params = {}) => api.get(`/sensors/${sensorId}/readings/`, { params }),
  create: (sensorId, data) => api.post(`/sensors/${sensorId}/readings/`, data),
};

// Enhanced response interceptor with token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
  
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        const refreshToken = localStorage.getItem('refresh');
        if (refreshToken) {
          try {
            const response = await api.post('/auth/refresh/', {
              refresh: refreshToken
            });
            const newAccessToken = response.data.access;
            localStorage.setItem('access', newAccessToken);
            
            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return api(originalRequest);
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            // If refresh fails, logout user
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            window.location.href = '/login';
          }
        } else {
          // No refresh token, redirect to login
          localStorage.removeItem('access');
          window.location.href = '/login';
        }
      }
      
      return Promise.reject(error);
    }
  );

export default api;