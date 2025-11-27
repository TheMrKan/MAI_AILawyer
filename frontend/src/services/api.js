import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Добавляем токен к запросам
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// обработка ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);

    if (error.response?.status === 401) {
      // Если токен невалидный, разлогиниваем пользователя
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');
      window.location.href = '/auth';
    }

    if (error.response) {
      const message = error.response.data?.detail || 'Произошла ошибка сервера';
      throw new Error(message);
    } else if (error.request) {
      throw new Error('Не удалось подключиться к серверу. Проверьте подключение к интернету.');
    } else {
      throw new Error('Произошла непредвиденная ошибка');
    }
  }
);

export const issueAPI = {
  async createIssue(description) {
    const response = await api.post('/issue/create', { text: description });
    return response.data;
  },

  async sendMessage(issueId, text) {
    const response = await api.post(`/issue/chat/${issueId}/`, { text });
    return response.data;
  },

  async getIssueStatus(issueId) {
    const response = await api.get(`/issue/${issueId}/`);
    return response.data;
  },

  async getChatHistory(issueId) {
    const response = await api.get(`/issue/${issueId}/`);
    return response.data;
  },

  async downloadDocument(issueId) {
    const response = await api.get(`/issue/${issueId}/download/`, {
      responseType: 'blob'
    });
    return response.data;
  }
};

export const userAPI = {
  async googleAuth() {
    window.location.href = `${API_BASE_URL}auth/google`;
  },

  async verifyToken(token) {
    const response = await api.post('/auth/token/verify', { token });
    return response.data;
  },

  async getProfile() {
    const response = await api.get('/user/profile');
    return response.data;
  },

  async updateProfile(userData) {
    const response = await api.put('/user/profile', userData);
    return response.data;
  },

  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    window.location.href = '/';
  }
};

export const handleAuthSuccess = (authData) => {
  if (authData.access_token) {
    localStorage.setItem('auth_token', authData.access_token);
  }
  if (authData.user) {
    localStorage.setItem('user', JSON.stringify(authData.user));
    return authData.user;
  }
  return null;
};

export default api;