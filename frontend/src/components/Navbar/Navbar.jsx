import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import './Navbar.scss';

const Navbar = ({ currentUser, onLogout }) => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <Link to="/" className="logo-link">
          <div className="logo-icon">
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M18.54 23.5a24.47 24.47 0 0 1 2.29-9.9 8.62 8.62 0 0 0 .73-3.25 8.71 8.71 0 0 0-8.31-8.85 8.61 8.61 0 0 0-8.9 8.61v.58l-1.77 3.89a1.49 1.49 0 0 0-.15.66A1.57 1.57 0 0 0 4 16.8h.35v1a2.86 2.86 0 0 0 2.87 2.87h1.91v2.83"/>
              <path d="M9.13 7.24h2.46a4.23 4.23 0 0 1 4.23 4.23v2.46h-2.45A4.23 4.23 0 0 1 9.13 9.7V7.24zM17.74 15.85 12 10.11"/>
            </svg>
          </div>
          <span className="logo-text">Claim-Composer AI</span>
        </Link>
      </div>

      <div className="navbar-center">
        <div className="nav-links">
          <Link
            to="/"
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            Главная
          </Link>
            <Link
            to="/about"
            className={`nav-link ${location.pathname === '/about' ? 'active' : ''}`}
          >
            О проекте
          </Link>
        </div>
      </div>

      <div className="navbar-right">
        {currentUser ? (
          <div className="user-menu">
            <button
              className="user-avatar"
              onClick={() => navigate('/account')}
              title="Мой профиль"
            >
              {currentUser.avatar ? (
                <img
                  src={currentUser.avatar}
                  alt="Аватар"
                  className="avatar-icon"
                  style={{ width: '32px', height: '32px', borderRadius: '50%', objectFit: 'cover' }}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.style.display = 'none';
                    e.target.parentElement.innerHTML = '<span class="avatar-icon">👤</span>';
                  }}
                />
              ) : (
                <span className="avatar-icon">{currentUser.name?.charAt(0) || '👤'}</span>
              )}
              <span className="user-name">{currentUser.name || 'Пользователь'}</span>
            </button>
          </div>
        ) : (
          <div className="auth-buttons">
            <Link 
              to="/signin" 
              className="nav-link"
            >
              Войти
            </Link>
            <Link 
              to="/signin" 
              className="nav-link signup"
            >
              Регистрация
            </Link>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;