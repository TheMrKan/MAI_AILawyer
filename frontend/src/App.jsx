import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage/HomePage';
import ChatPage from './pages/ChatPage/ChatPage';
import AccountPage from './pages/AccountPage/AccountPage';
import AuthPage from './pages/AuthPage/AuthPage';
import AboutPage from './pages/AboutPage/AboutPage';
import './styles/globals.scss';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat/:requestId" element={<ChatPage />} />
          <Route path="/account" element={<AccountPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/signin" element={<AuthPage />} />
          <Route path="*" element={<div>Страница не найдена</div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;