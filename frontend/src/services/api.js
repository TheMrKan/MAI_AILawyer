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

    if (error.response?.status === 429) {
      throw {name: "RateLimitError", message: ""};
    }

    if (error.response) {
      // Сервер от ветил  с ошибкой пример
      const message = error.response.data?.detail || 'Произошла ошибка сервера';
      throw new Error(message);
    } else if (error.request) {
      // Запрос был сделан, но ответ не получен  пример
      throw new Error('Не удалось подключиться к серверу. Проверьте подключение к интернету.');
    } else {
      // Что-то по шло не так при настройке з апроса
      throw new Error('Произошла непредвиденная ошибка');
    }
  }
);

export const issueAPI = {
  // новый issue
  async createIssue(description) {
    try {
      // Временно генерируем случайный ID, пока бэкенд не реализует создание ЕГорррррр
      const response = await api.post("/issue/create/", { "text": description });
      return { issue_id: response.data["issue_id"] };
    } catch (error) {
      console.error('Error creating issue:', error);
      throw error;
    }
  },

  // Отправка сообщения в чат
  async sendMessage(issueId, text) {
    try {
      const response = await api.post(`/issue/${issueId}/chat/`, { text });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  // Получение истории сообщений
  async getChatHistory(issueId) {
    try {
      // Временная заглушка
      const response = await api.get(`/issue/${issueId}/chat/`, {  });
      return response.data;
    } catch (error) {
      console.error('Error getting chat history:', error);
      throw error;
    }
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
  console.log('Auth data received:', authData); // Для отладки

  if (authData.access_token) {
    localStorage.setItem('auth_token', authData.access_token);
  }
  if (authData.user) {
    // Берем данные из Google
    const googleFirstName = authData.user.first_name || '';
    const googleLastName = authData.user.last_name || '';
    const googleEmail = authData.user.email || '';
    const googleAvatar = authData.user.avatar_url || '';

    // Формируем имя для отображения
    const displayName = googleFirstName && googleLastName
      ? `${googleFirstName} ${googleLastName}`
      : googleFirstName || googleLastName || googleEmail.split('@')[0] || 'Пользователь';

    const userData = {
      id: authData.user.id,
      email: googleEmail,
      name: displayName,
      firstName: googleFirstName,
      lastName: googleLastName,
      avatar: googleAvatar,
      joinDate: new Date().toLocaleDateString('ru-RU'),
      phone: ''
    };

    console.log('Processed user data:', userData); // Для отладки
    localStorage.setItem('user', JSON.stringify(userData));
    return userData;
  }
  return null;
};

export default api;