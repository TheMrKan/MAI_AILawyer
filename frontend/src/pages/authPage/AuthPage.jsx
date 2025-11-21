import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import './AuthPage.scss';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    phone: '',
    name: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Валидацияс
    if (!isLogin && formData.password !== formData.confirmPassword) {
      alert('Пароли не совпадают');
      setIsLoading(false);
      return;
    }

    try {
      //API запрос обманка
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      //  API call
      console.log('Auth data:', formData);
      
      // Успешная авторизация
      localStorage.setItem('user', JSON.stringify({
        name: formData.name || 'Пользователь',
        email: formData.email,
        isAuthenticated: true
      }));
      
      navigate('/account');
    } catch (error) {
      console.error('Auth error:', error);
      alert('Произошла ошибка. Попробуйте снова.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialAuth = (provider) => {
    alert(`Авторизация через ${provider} будет реализована позже`);
  };

  return (
    <div className="auth-page">
      <Navbar />
      
      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>{isLogin ? 'Вход в систему' : 'Регистрация'}</h1>
            <p>{isLogin ? 'Войдите в ваш аккаунт' : 'Создайте новый аккаунт'}</p>
          </div>

          <form onSubmit={handleSubmit} className="auth-form">
            {!isLogin && (
              <div className="form-group">
                <label htmlFor="name">Имя и фамилия</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Иван Иванов"
                  required={!isLogin}
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your@email.com"
                required
              />
            </div>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="phone">Номер телефона</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="+7 (999) 999-99-99"
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="password">Пароль</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Введите пароль"
                required
                minLength="6"
              />
            </div>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="confirmPassword">Подтвердите пароль</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Повторите пароль"
                  required={!isLogin}
                />
              </div>
            )}

            <Button 
              type="submit" 
              className="auth-button"
              loading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? 'Обработка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')}
            </Button>
          </form>

          <div className="auth-switch">
            <p>
              {isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}{' '}
              <button 
                type="button" 
                className="switch-button"
                onClick={() => setIsLogin(!isLogin)}
              >
                {isLogin ? 'Зарегистрироваться' : 'Войти'}
              </button>
            </p>
          </div>

          <div className="divider">
            <span>или</span>
          </div>

          <div className="social-auth">
            <h3>Войти через соцсети</h3>
            <div className="social-buttons">
              <Button 
                variant="secondary" 
                className="social-button google"
                onClick={() => handleSocialAuth('Google')}
              >
                <span className="social-icon">🔍</span>
                Google
              </Button>
              <Button 
                variant="secondary" 
                className="social-button yandex"
                onClick={() => handleSocialAuth('Yandex')}
              >
                <span className="social-icon">Я</span>
                Yandex
              </Button>
              <Button 
                variant="secondary" 
                className="social-button vk"
                onClick={() => handleSocialAuth('VK')}
              >
                <span className="social-icon">ВК</span>
                VK
              </Button>
            </div>
          </div>

          <div className="auth-footer">
            <p>
              Нажимая кнопку, вы соглашаетесь с{' '}
              <Link to="/privacy">политикой конфиденциальности</Link> и{' '}
              <Link to="/terms">условиями использования</Link>
            </p>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default AuthPage;