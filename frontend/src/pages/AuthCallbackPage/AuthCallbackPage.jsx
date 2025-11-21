import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { handleAuthSuccess } from '../../services/api';
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

        if (dataParam) {
          try {
            // Декодируем данные из URL
            const authData = JSON.parse(decodeURIComponent(dataParam));

            // Сохраняем токен и пользователя
            const user = handleAuthSuccess(authData);

            if (user) {
              setStatus('success');
              // Перенаправляем на главную страницу через 2 секунды
              setTimeout(() => {
                navigate('/', { replace: true });
              }, 2000);
            } else {
              setStatus('error');
            }
          } catch (parseError) {
            console.error('Error parsing auth data:', parseError);
            setStatus('error');
          }
        } else {
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
            <p>Вы будете перенаправлены на главную страницу...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="auth-status error">
            <div className="error-icon">❌</div>
            <h2>Ошибка авторизации</h2>
            <p>Не удалось завершить вход в систему. Пожалуйста, попробуйте снова.</p>
            <button
              className="retry-button"
              onClick={() => navigate('/auth')}
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