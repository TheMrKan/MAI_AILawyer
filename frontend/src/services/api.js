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
      const hadToken = !!localStorage.getItem('auth_token');

      localStorage.removeItem('auth_token');
      localStorage.removeItem('user');

      // ❗ Редирект ТОЛЬКО если был реальный логин
      if (hadToken) {
        window.location.href = '/signin';
      }

      // ❗ Для анонимов просто пробрасываем ошибку
      return Promise.reject(error);
    }

    if (error.response?.status === 429) {
      throw { name: "RateLimitError", message: "" };
    }

    if (error.response) {
      throw new Error(
        error.response.data?.detail || 'Произошла ошибка сервера'
      );
    }

    if (error.request) {
      throw new Error('Нет соединения с сервером');
    }

    throw new Error('Неизвестная ошибка');
  }
);


export const issueAPI = {
  async createIssue(description) {
  const response = await api.post("/issue/create/", { text: description });

  const token = response.headers['x-auth-token'];
  const isAnonymous = response.headers['x-anonymous'] === 'true';

  if (token) {
    localStorage.setItem('auth_token', token);
    api.defaults.headers.Authorization = `Bearer ${token}`;

    if (isAnonymous) {
      const anonUser = {
        id: null,
        name: 'Гость',
        isAnonymous: true,
      };
      localStorage.setItem('user', JSON.stringify(anonUser));
    }
  }

  return { issue_id: response.data.issue_id };
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
  },

  // Скачивание документа
  async downloadDocument(issueId) {
      try {
        const response = await api.get(`/issue/${issueId}/download/`, {
          responseType: 'arraybuffer', // Меняем на arraybuffer
          timeout: 60000,
          headers: {
            'Accept': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
          }
        });

        return response;
      } catch (error) {
        console.error('Error downloading document:', error);

        // Более информативные ошибки
        if (error.response?.status === 404) {
          throw new Error('Документ не найден');
        } else if (error.response?.status === 403) {
          throw new Error('Нет доступа к документу');
        } else if (error.response?.status === 500) {
          throw new Error('Ошибка сервера при генерации документа');
        }

        throw error;
      }
    },

};

export const userAPI = {
  async googleAuth() {
    window.location.href = `${API_BASE_URL}/auth/google`;
  },

  async getUserDocuments() {
    try {
      const response = await api.get('/profile/documents/');
      return response.data;
    } catch (error) {
      console.error('Error loading documents:', error);
      throw error;
    }
  },

  async getMe() {
    const response = await api.get('/profile/me');
    return response.data;
  },

  logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    window.location.href = '/auth';
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