import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { handleAuthSuccess, userAPI } from '../../services/api';
import './AuthCallbackPage.scss';

const AuthCallbackPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    const processAuth = async () => {
      try {
        const error = searchParams.get('error');
        const dataParam = searchParams.get('data');

        if (error) {
          console.error('Auth error:', error);
          setStatus('error');
          return;
        }

        if (!dataParam) {
          setStatus('error');
          return;
        }

        try {
          // Декодируем данные из URL
          const authData = JSON.parse(decodeURIComponent(dataParam));

          // Сохраняем токен
          handleAuthSuccess(authData);

          // Теперь тянем профиль
          try {
            const user = await userAPI.getMe();
            localStorage.setItem('user', JSON.stringify(user));

            setStatus('success');
            setTimeout(() => navigate('/', { replace: true }), 1000);
          } catch (e) {
            console.error('Failed to fetch /me:', e);
            setStatus('error');
          }

        } catch (parseError) {
          console.error('Error parsing auth data:', parseError);
          setStatus('error');
        }

      } catch (err) {
        console.error('Auth processing error:', err);
        setStatus('error');
      }
    };

    processAuth();
  }, [searchParams, navigate]);

  return (
    <div className="auth-callback-page">
      <div className="auth-callback-container">
        {status === 'loading' && (
          <div className="auth-status loading">
            <div className="spinner"></div>
            <h2>Завершение авторизации...</h2>
            <p>Пожалуйста, подождите</p>
          </div>
        )}

        {status === 'success' && (
          <div className="auth-status success">
            <div className="success-icon">✅</div>
            <h2>Авторизация успешна!</h2>
            <p>Вы будете перенаправлены в личный кабинет...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="auth-status error">
            <div className="error-icon">❌</div>
            <h2>Ошибка авторизации</h2>
            <p>Не удалось завершить вход в систему. Пожалуйста, попробуйте снова.</p>
            <button
              className="retry-button"
              onClick={() => navigate('/signin')}
            >
              Попробовать снова
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuthCallbackPage;
