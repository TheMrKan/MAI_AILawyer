import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import { issueAPI } from '../../services/api';
import './ChatPage.scss';

const ChatPage = () => {
  const { requestId } = useParams();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isChatEnded, setIsChatEnded] = useState(false);
  const [documentData, setDocumentData] = useState(null);
  const messagesEndRef = useRef(null);
  const [isSuccess, setIsSuccess] = useState(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadCalled = useRef(false);

    useEffect(() => {
      loadChat();
    }, []);

    const loadChat = () => {
      if (loadCalled.current) return;
      loadCalled.current = true;

      issueAPI.getChatHistory(requestId).then((history) => {
        const newMessages = history.new_messages.map(msg => ({
          id: Date.now() + Math.random(),
          text: msg.text,
          sender: msg.role === 'user' ? 'user' : 'ai',
          timestamp: new Date()
        }));

        setMessages(prev => [...prev, ...newMessages]);

        setIsChatEnded(history.is_ended);
        setIsSuccess(history.success);
      });
    };

  const processApiResponse = (response) => {
    const messagesToAdd = response.new_messages.slice(1);
    const newMessages = messagesToAdd.map(msg => ({
      id: Date.now() + Math.random(),
      text: msg.text,
      sender: msg.role === 'user' ? 'user' : 'ai',
      timestamp: new Date()
    }));

    setMessages(prev => [...prev, ...newMessages]);
    setIsChatEnded(response.is_ended);

    // Обновляем success статус
    if (response.success !== undefined) {
      setIsSuccess(response.success);
    }
  };

  const addErrorMessage = (error) => {
    let text = 'Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте снова.';
    if (error.name === "RateLimitError") {
      text = "Использование нашего сервиса полностью бесплатно, поэтому мы вынуждены экономить.\nОдин из сервисов сейчас не справляется, пожалуйста, попробуйте позднее."
    }

    const errorMessage = {
      id: Date.now(),
      text: text,
      sender: 'ai',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, errorMessage]);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!currentMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: currentMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');

    setIsLoading(true);
    try {
      const response = await issueAPI.sendMessage(requestId, userMessage.text);
      processApiResponse(response);
    } catch (error) {
      console.error('Error sending message:', error);
      addErrorMessage(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadDocument = async () => {
      setIsLoading(true);

      try {
        const response = await issueAPI.downloadDocument(requestId);

        // Проверяем, что ответ содержит данные
        if (!response.data || response.data.byteLength === 0) {
          throw new Error('Пустой ответ от сервера');
        }

        // Создаем Blob
        const blob = new Blob([response.data], {
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        });

        // Создаем URL для скачивания
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `issue_${requestId}_result.docx`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);



      } catch (err) {
        console.error('Ошибка при скачивании:', err);
        alert('Не удалось скачать документ. Пожалуйста, попробуйте позже.');
      } finally {
        setIsLoading(false);
      }
    };

  const handleContinueEditing = () => {
    setIsChatEnded(false);
    setCurrentMessage('Хочу внести правки в документ');
  };

  const handleNewDocument = () => {
    navigate('/');
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="chat-page">
      <Navbar />

      <div className="chat-container">
        {/* Хедер чата */}
        <div className="chat-header">
          <div className="chat-info">
            <Button
              variant="text"
              onClick={() => navigate('/')}
              className="back-button"
            >
              ← Назад к главной
            </Button>
            <h1>Диалог с AI-помощником</h1>
            <p>ID запроса: <span className="request-id">{requestId}</span></p>
          </div>

          <div className="chat-actions">
            <Button
              variant="secondary"
              onClick={() => navigate('/account')}
              size="small"
            >
              📋 Мои документы
            </Button>
          </div>
        </div>

        {/* Область сообщений */}
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <div className="empty-icon">💬</div>
              <h3>Начинаем анализ вашей проблемы</h3>
              <p>AI-помощник обрабатывает ваше обращение...</p>
              <LoadingSpinner size="medium" text="Подключаемся к сервису" />
            </div>
          ) : (
            <div className="messages-container">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`message ${message.sender === 'user' ? 'message-user' : 'message-ai'}`}
                >
                  <div className="message-avatar">
                    {message.sender === 'user' ? '👤' : '🤖'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{message.text}</div>
                    <div className="message-time">
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message message-ai">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span>AI-помощник печатает</span>
                      <div className="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>


        {isChatEnded && (
          <div className="document-section">
            {isSuccess ? (
              <div className="document-card">
                <div className="document-header">
                  <div className="document-icon">
                    🎉
                  </div>
                  <div className="document-info">
                    <h3>Ваш документ готов!</h3>
                    <p>AI-помощник подготовил документ для вашей проблемы</p>
                  </div>
                </div>

                <div className="document-details">
                  <div className="detail-item">
                    <span className="label">Статус:</span>
                    <span className="value">Готов к скачиванию</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Анализ:</span>
                    <span className="value">Проблема подтверждена</span>
                  </div>
                </div>

                <div className="document-actions">
                  <Button
                    variant="primary"
                    onClick={handleDownloadDocument}
                    loading={isLoading}
                    className="action-btn"
                  >
                    📥 Скачать DOCX
                  </Button>
                </div>
              </div>
            ) : (
             <div className="no-document-message">
                <p>
                  <strong>AI-помощник не нашел юридической проблемы, требующей оформления документа.</strong>
                  <br />
                  Возможно, ваша ситуация уже решена или не требует юридического вмешательства.
                </p>
                <div className="document-actions">
                  <Button
                    variant="secondary"
                    onClick={() => navigate('/')}
                    className="action-btn"
                  >
                    👉 Создать новый запрос
                  </Button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Форма ввода сообщения */}
        {!isChatEnded && (
          <form onSubmit={handleSendMessage} className="chat-input-form">
            <div className="input-container">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder="Введите ваш ответ или задайте вопрос..."
                className="chat-input"
                disabled={isLoading}
              />
              <Button
                type="submit"
                className="send-button"
                disabled={isLoading || !currentMessage.trim()}
                loading={isLoading}
              >
                Отправить
              </Button>
            </div>
            <div className="input-hint">
              Нажмите Enter для отправки сообщения
            </div>
          </form>
        )}

        {/* Быстрые действия после завершения */}
        {isChatEnded && (
          <div className="quick-actions">
            <div className="actions-title">Что дальше?</div>
            <div className="actions-grid">
              <div className="action-card" onClick={handleNewDocument}>
                <div className="action-icon">🆕</div>
                <h4>Новый документ</h4>
                <p>Создайте следующее обращение</p>
              </div>
              <div className="action-card" onClick={() => navigate('/account')}>
                <div className="action-icon">📋</div>
                <h4>Мои документы</h4>
                <p>Перейти к истории обращений</p>
              </div>
              <div className="action-card">
                <div className="action-icon">ℹ️</div>
                <h4>Помощь</h4>
                <p>Как отправить документ</p>
              </div>
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default ChatPage;