import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import { userAPI } from '../../services/api';
import './AuthPage.scss';

const AuthPage = () => {
  const navigate = useNavigate();

  const handleGoogleAuth = () => {
    userAPI.googleAuth();
  };

  const handleSocialAuth = (provider) => {
    if (provider === 'Google') {
      handleGoogleAuth();
    } else {
      alert(`Авторизация через ${provider} будет реализована позже`);
    }
  };

  return (
    <div className="auth-page">
      <Navbar />

      <div className="auth-container">
        <div className="auth-card">
          <div className="auth-header">
            <h1>Вход в систему</h1>
            <p>Выберите способ авторизации</p>
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
              <a href="/privacy">политикой конфиденциальности</a> и{' '}
              <a href="/terms">условиями использования</a>
            </p>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default AuthPage;