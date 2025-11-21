import React from 'react';
import './Footer.scss';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>Claim-Composer AI</h3>
          <p>Юридический помощник с искусственным интеллектом</p>
          <div className="social-links">
            <a href="#" className="social-link">📘</a>
            <a href="#" className="social-link">🐦</a>
            <a href="#" className="social-link">📷</a>
          </div>
        </div>
        
        <div className="footer-section">
          <h4>Возможности</h4>
          <ul>
            <li><a href="/">Создание жалоб</a></li>
            <li><a href="/">Юридические консультации</a></li>
            <li><a href="/">Шаблоны документов</a></li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>Поддержка</h4>
          <ul>
            <li><a href="/about">О проекте</a></li>
            <li><a href="#">Помощь</a></li>
            <li><a href="#">Контакты</a></li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>Правовая информация</h4>
          <ul>
            <li><a href="#">Политика конфиденциальности</a></li>
            <li><a href="#">Условия использования</a></li>
            <li><a href="#">Cookie</a></li>
          </ul>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>&copy; 2025 Сlaim-Composer AI. Все права защищены.</p>
      </div>
    </footer>
  );
};

export default Footer;