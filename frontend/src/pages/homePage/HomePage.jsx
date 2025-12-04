import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import Modal from '../../components/Modal/Modal';
import { issueAPI, userAPI } from '../../services/api';
import './HomePage.scss';

const HomePage = () => {
  const [problemDescription, setProblemDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const navigate = useNavigate();

  // Проверяем авторизацию при загрузке и обновляем состояние
  useEffect(() => {
    const checkAuth = () => {
      const user = localStorage.getItem('user');
      if (user) {
        try {
          setCurrentUser(JSON.parse(user));
        } catch (error) {
          console.error('Error parsing user data:', error);
          localStorage.removeItem('user');
          localStorage.removeItem('auth_token');
        }
      }
    };

    // Проверяем авторизацию при загрузке
    checkAuth();

    // Слушаем события изменения localStorage (для обновления при авторизации из других вкладок)
    window.addEventListener('storage', checkAuth);

    return () => {
      window.removeEventListener('storage', checkAuth);
    };
  }, []);

  // Обработчик для обновления при возврате на страницу
  useEffect(() => {
    const handlePageShow = (event) => {
      if (event.persisted) {
        const user = localStorage.getItem('user');
        if (user) {
          setCurrentUser(JSON.parse(user));
        }
      }
    };

    window.addEventListener('pageshow', handlePageShow);
    return () => {
      window.removeEventListener('pageshow', handlePageShow);
    };
  }, []);

  // Проверяем авторизацию при каждом рендере (на случай если пользователь авторизовался в другой вкладке)
  useEffect(() => {
    const user = localStorage.getItem('user');
    if (user && !currentUser) {
      setCurrentUser(JSON.parse(user));
    }
  }, [currentUser]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!problemDescription.trim()) {
      alert('Пожалуйста, опишите вашу проблему');
      return;
    }

    // Если пользователь не авторизован, показываем модалку
    if (!currentUser) {
      setShowAuthModal(true);
      return;
    }

    setIsLoading(true);

    try {
      const response = await issueAPI.createIssue(problemDescription);
      navigate(`/chat/${response.issue_id}`);
    } catch (error) {
      console.error('Error creating issue:', error);

      // Если ошибка авторизации, разлогиниваем и просим авторизоваться снова
      if (error.message.includes('401') || error.message.includes('токен')) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        setCurrentUser(null);
        setShowAuthModal(true);
        alert('Сессия истекла. Пожалуйста, войдите снова.');
      } else if (error.name === "RateLimitError") {
        alert("Использование нашего сервиса полностью бесплатно, поэтому мы вынуждены экономить. Один из сервисов сейчас не справляется, пожалуйста, попробуйте позднее.");
      } else {
        alert('Произошла ошибка при создании запроса. Пожалуйста, попробуйте снова.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickStart = (example) => {
    setProblemDescription(example);
  };

  const handleGoogleAuth = () => {
    userAPI.googleAuth();
  };

  const handleLogout = () => {
    userAPI.logout();
    setCurrentUser(null);
  };

  return (
    <div className="home-page">
      <Navbar currentUser={currentUser} onLogout={handleLogout} />

      <main className="main-content">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <div className="hero-text">
              <h1 className="hero-title">
                Создайте юридически грамотное обращение за минуты
              </h1>
              <p className="hero-subtitle">
                AI-помощник анализирует вашу проблему и генерирует готовые документы
                для обращения в государственные органы и организации
              </p>

              {currentUser && (
                <div className="user-welcome">
                  <p>Добро пожаловать, {currentUser.name || currentUser.email}!</p>
                </div>
              )}

              <div className="hero-stats">
                <div className="stat">
                  <div className="stat-number">2-3 мин</div>
                  <div className="stat-label">Среднее время генерации</div>
                </div>
              </div>
            </div>

            <div className="hero-visual">
              <div className="floating-card card-1">
                <div className="card-icon">⚖️</div>
                <p>Юридические консультации</p>
              </div>
              <div className="floating-card card-2">
                <div className="card-icon">🏛️</div>
                <p>Исковые заявления</p>
              </div>
              <div className="floating-card card-3">
                <div className="card-icon">📝</div>
                <p>Претензии организациям</p>
              </div>
            </div>
          </div>
        </section>

        {/* Problem Form Section */}
        <section className="form-section">
          <div className="container">
            <div className="section-header">
              <h2>Опишите вашу проблему</h2>
              <p>AI-помощник проанализирует ситуацию и предложит решение</p>
            </div>

            <form onSubmit={handleSubmit} className="problem-form">
              <div className="textarea-container">
                <label htmlFor="problem-description" className="textarea-label">
                  Подробно опишите ситуацию:
                </label>
                <textarea
                  id="problem-description"
                  value={problemDescription}
                  onChange={(e) => setProblemDescription(e.target.value)}
                  placeholder="Например: 'Меня принуждают к переработкам без соответствующей компенсации, какую жалобу написать на начальника????'"
                  className="problem-textarea"
                  rows="8"
                  disabled={isLoading || !currentUser}
                />
                <div className="textarea-footer">
                  <span className="char-count">
                    {problemDescription.length} символов
                  </span>
                  <div className="textarea-actions">
                    <button
                      type="button"
                      className="clear-btn"
                      onClick={() => setProblemDescription('')}
                      disabled={!problemDescription.trim()}
                    >
                      Очистить
                    </button>
                  </div>
                </div>
              </div>

                {!currentUser && (
                <div className="auth-notice" style={{ marginBottom: '20px', textAlign: 'center' }}>
                  <span>⚠️ Для создания документов требуется авторизация</span>
                </div>
              )}

              {currentUser ? (
                <Button
                  type="submit"
                  loading={isLoading}
                  disabled={isLoading || !problemDescription.trim()}
                  className="submit-button"
                >
                  {isLoading ? 'Обработка...' : 'Создать документ'}
                </Button>
              ) : (
                <Button
                  type="button"
                  variant="primary"
                  onClick={() => setShowAuthModal(true)}
                  className="submit-button"
                >
                  Войти для создания документа
                </Button>
              )}
            </form>

            {/* Quick Examples */}-
          </div>
        </section>

        {/* Features Section */}
        <section className="features-section">
          <div className="container">
            <div className="section-header">
              <h2>Почему выбирают AI-ASSISTANT</h2>
              <p>Современный подход к решению юридических проблем</p>
            </div>

            <div className="features-grid">
              <div className="feature-card">
                <div className="feature-icon">⚡</div>
                <h3>Быстро</h3>
                <p>Генерация документов за 2-3 минуты вместо часов самостоятельной работы</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">⚖️</div>
                <h3>Юридически грамотно</h3>
                <p>Все документы соответствуют актуальному законодательству РФ</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🎯</div>
                <h3>Точно</h3>
                <p>Умный AI понимает контекст и подбирает оптимальное решение</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🛡️</div>
                <h3>Безопасно</h3>
                <p>Ваши данные защищены и не передаются третьим лицам</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">💼</div>
                <h3>Профессионально</h3>
                <p>Документы готовы к отправке в государственные органы</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">📱</div>
                <h3>Удобно</h3>
                <p>Общайтесь в свободном формате</p>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="how-it-works">
          <div className="container">
            <div className="section-header">
              <h2>Как это работает</h2>
              <p>Всего 4 простых шага до решения вашей проблемы</p>
            </div>

            <div className="steps">
              <div className="step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h3>Опишите проблему</h3>
                  <p>Расскажите о своей ситуации простыми словами</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h3>AI анализирует</h3>
                  <p>Наш ИИ изучает проблему и подбирает подходящие законы</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Получите документ</h3>
                  <p>Готовый документ в формате DOCX</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h3>Отправляйте</h3>
                  <p>Распечатайте и отправьте в нужную инстанцию</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />

      {/* Auth Modal */}
      <Modal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        title="Требуется авторизация"
        size="small"
      >
        <div className="auth-modal-content">
          <p>Для создания документов необходимо войти в систему через Google</p>
          <div className="auth-modal-actions">
            <Button
              variant="primary"
              onClick={handleGoogleAuth}
            >
              Войти через Google
            </Button>
            <Button
              variant="text"
              onClick={() => setShowAuthModal(false)}
            >
              Отмена
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default HomePage;