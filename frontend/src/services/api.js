import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// обработка ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
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
      const response = await api.post('/issue/create', { 
        text: description  // МЕНЯЕМ "description" на "text"
      });
      return response.data;
    } catch (error) {
      console.error('Error creating issue:', error);
      throw error;
    }
  },

  // Отправка сообщения в чат - ИСПРАВЛЕННАЯ ВЕРСИЯ
   async sendMessage(issueId, messageData) {
    try {
      // МЕНЯЕМ с /issues/{issue_id}/messages/ на /issue/{issue_id}/chat/
      const response = await api.post(`/issue/${issueId}/chat/`, messageData);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  // Проверка статуса issue
  async getIssueStatus(issueId) {
    try {
      const response = await api.get(`/issues/${issueId}/`);
      return response.data;
    } catch (error) {
      console.error('Error getting issue status:', error);
      throw error;
    }
  },

  // Получение истории сообщений
  async getChatHistory(issueId) {
    try {
      const response = await api.get(`/issues/${issueId}/messages/`);
      return response.data;
    } catch (error) {
      console.error('Error getting chat history:', error);
      throw error;
    }
  }
};

// User API (заглушки для будущей реализации)
export const userAPI = {
  async login(email, password) {
    // Заглушка для авторизации
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          user: {
            id: 1,
            name: 'Иван Иванов',
            email: email,
            avatar: '👤'
          },
          token: 'fake-jwt-token'
        });
      }, 2000);
    });
  },

  async register(userData) {
    // Заглушка для регистрации
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          user: {
            id: 1,
            name: userData.name,
            email: userData.email,
            avatar: '👤'
          },
          token: 'fake-jwt-token'
        });
      }, 2000);
    });
  },

  async getProfile() {
    // Заглушка для получения профиля
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          id: 1,
          name: 'Иван Иванов',
          email: 'ivan@example.com',
          phone: '+7 (999) 123-45-67',
          joinDate: '15 января 2024',
          avatar: '👤'
        });
      }, 1000);
    });
  }
};

export default api;