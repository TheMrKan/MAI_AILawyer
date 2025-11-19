import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import Modal from '../../components/Modal/Modal';
import { issueAPI } from '../../services/api';
import './HomePage.scss';

const HomePage = () => {
  const [problemDescription, setProblemDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [currentUser] = useState({
    isAuthenticated: true, 
    // временно true для теста
    name: 'Иван Иванов'
  });
  
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!problemDescription.trim()) {
      alert('Пожалуйста, опишите вашу проблему');
      return;
    }

    // Если пользователь не авторизован, показываем модалку
    if (!currentUser.isAuthenticated) {
      setShowAuthModal(true);
      return;
    }

    setIsLoading(true);

    try {
      const response = await issueAPI.createIssue(problemDescription);
      navigate(`/chat/${response.issue_id}`);
    } catch (error) {
      console.error('Error creating issue:', error);
      alert('Произошла ошибка при создании запроса. Пожалуйста, попробуйте снова.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickStart = (example) => {
    setProblemDescription(example);
  };

  const quickExamples = [
    {
      title: 'Возврат товара',
      description: 'Магазин отказывается принимать товар обратно',
      example: 'Купил телефон две недели назад, обнаружил брак. Магазин отказывается принимать товар на возврат, ссылаясь на то, что гарантийный срок истек.'
    },
    {
      title: 'Некачественные услуги',
      description: 'Исполнитель выполнил работу плохо',
      example: 'Заказал ремонт в квартире, подрядчик выполнил работу с нарушениями: кривые стены, протекают трубы. Отказывается исправлять недостатки.'
    },
    {
      title: 'Проблемы с ЖКХ',
      description: 'Управляющая компания не решает проблемы',
      example: 'В квартире постоянно течет крыша, управляющая компания игнорирует заявки. Помещение повреждено, жить невозможно.'
    }
  ];

  return (
    <div className="home-page">
      <Navbar />
      
      <main className="main-content">
        {/* Hero Section */}
        <section className="hero-section">
          <div className="hero-content">
            <div className="hero-text">
              <h1 className="hero-title">
                Создайте юридически грамотную жалобу за минуты
              </h1>
              <p className="hero-subtitle">
                AI-помощник анализирует вашу проблему и генерирует готовые документы 
                для обращения в государственные органы и организации
              </p>
              
              <div className="hero-stats">
                <div className="stat">
                  <div className="stat-number">500+</div>
                  <div className="stat-label">успешных обращений</div>
                </div>
                <div className="stat">
                  <div className="stat-number">98%</div>
                  <div className="stat-label">положительных решений</div>
                </div>
                <div className="stat">
                  <div className="stat-number">24/7</div>
                  <div className="stat-label">доступность</div>
                </div>
              </div>
            </div>
            
            <div className="hero-visual">
              <div className="floating-card card-1">
                <div className="card-icon">⚖️</div>
                <p>Жалобы в Роспотребнадзор</p>
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
                  placeholder="Например: 'Мне не возвращают деньги за некачественный товар, купленный две недели назад. Магазин отказывается принимать претензию, ссылаясь на то, что товар был в использовании...'"
                  className="problem-textarea"
                  rows="8"
                  disabled={isLoading}
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
              
              <Button 
                type="submit" 
                loading={isLoading}
                disabled={isLoading || !problemDescription.trim()}
                className="submit-button"
              >
                {isLoading ? 'Обработка...' : 'Создать документ'}
              </Button>
            </form>

            {/* Quick Examples */}
            <div className="quick-examples">
              <h3>Примеры типичных ситуаций:</h3>
              <div className="examples-grid">
                {quickExamples.map((example, index) => (
                  <div 
                    key={index}
                    className="example-card"
                    onClick={() => handleQuickStart(example.example)}
                  >
                    <div className="example-icon">
                      {example.title === 'Возврат товара' && '🛍️'}
                      {example.title === 'Некачественные услуги' && '🔧'}
                      {example.title === 'Проблемы с ЖКХ' && '🏠'}
                    </div>
                    <h4>{example.title}</h4>
                    <p>{example.description}</p>
                    <Button variant="text" size="small">
                      Использовать пример →
                    </Button>
                  </div>
                ))}
              </div>
            </div>
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
                <div className="feature-icon">📱</div>
                <h3>Удобно</h3>
                <p>Работает на компьютере, планшете и телефоне без установки ПО</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">🛡️</div>
                <h3>Безопасно</h3>
                <p>Ваши данные защищены и не передаются третьим лицам</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">💡</div>
                <h3>Умный AI</h3>
                <p>Искусственный интеллект анализирует и предлагает оптимальное решение</p>
              </div>
              <div className="feature-card">
                <div className="feature-icon">📊</div>
                <h3>Статистика успеха</h3>
                <p>98% обращений приводят к положительному решению проблемы</p>
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
                  <p>Наш ИИ изучает проблему и подбирает relevantные законы</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Получите документ</h3>
                  <p>Готовый документ в форматах DOCX или PDF</p>
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
          <p>Для создания документов необходимо войти в систему</p>
          <div className="auth-modal-actions">
            <Button 
              variant="primary"
              onClick={() => navigate('/signin')}
            >
              Войти
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