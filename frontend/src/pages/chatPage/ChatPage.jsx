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
  const hasSentInitial = useRef(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  
  // ---------- ЕДИНАЯ ФУНКЦИЯ ОТПРАВКИ ----------
 const sendMessageToBackend = async (text) => {
  console.log("=== НАЧАЛО ОТПРАВКИ ===");
  console.log("📝 Текст:", text);
  console.log("🆔 requestId:", requestId);
  console.log("⏳ isLoading:", isLoading);
  console.log("❌ isChatEnded:", isChatEnded);

  if (!text.trim()) {
    console.log("❌ Текст пустой - выход");
    return;
  }
  if (isLoading) {
    console.log("❌ Уже идет загрузка - выход");
    return;
  }
  if (!requestId) {
    console.log("❌ Нет requestId - выход");
    return;
  }

  setIsLoading(true);

  try {
    console.log("🟡 Вызываем issueAPI.sendMessage...");
    console.log("📤 Параметры:", { requestId, text });
    
     const response = await issueAPI.sendMessage(requestId, { 
      text: text 
    });
    console.log("✅ УСПЕХ: Ответ от API:", response);
    
    processApiResponse(response);
  } catch (error) {
    console.error("❌ ОШИБКА:", error);
    console.error("❌ Response data:", error.response?.data);
    console.error("❌ Response status:", error.response?.status);
    console.error("❌ Response headers:", error.response?.headers);
    addErrorMessage();
  } finally {
    setIsLoading(false);
    console.log("=== КОНЕЦ ОТПРАВКИ ===");
  }
};



  // ---------- ОБРАБОТКА ОТВЕТА ----------
  const processApiResponse = (response) => {
    if (!response || !Array.isArray(response.new_messages)) return;

    const newMessages = response.new_messages.map(msg => ({
      id: Date.now() + Math.random(),
      text: msg.text,
      sender: msg.role === "user" ? "user" : "ai",
      timestamp: new Date()
    }));

    setMessages(prev => [...prev, ...newMessages]);
    setIsChatEnded(response.is_ended);

    if (response.is_ended) prepareDocumentData();
  };


  // ---------- СООБЩЕНИЕ ОБ ОШИБКЕ ----------
  const addErrorMessage = () => {
    setMessages(prev => [
      ...prev,
      {
        id: Date.now(),
        text: "Произошла ошибка. Попробуйте снова.",
        sender: "ai",
        timestamp: new Date()
      }
    ]);
  };


  // ---------- ДАННЫЕ ГОТОВОГО ДОКУМЕНТА ----------
  const prepareDocumentData = () => {
    setDocumentData({
      title: "Претензия о возврате денежных средств",
      type: "Жалоба",
      recipient: 'Магазин "Электроник"',
      date: new Date().toLocaleDateString("ru-RU"),
      content: "Полный текст документа..."
    });
  };


  // ---------- ОТПРАВКА ИЗ ФОРМЫ ----------
  const handleSendMessage = (e) => {
  e.preventDefault();
  if (!currentMessage.trim()) return;

  const userMessage = {
    id: Date.now(),
    text: currentMessage,
    sender: "user",
    timestamp: new Date()
  };

  setMessages(prev => [...prev, userMessage]);

  const msg = currentMessage;  
  setCurrentMessage("");

  // КРИТИЧЕСКИЙ ВЫЗОВ: отправляем на бэк
  sendMessageToBackend(msg);
};



  // ---------- СКАЧИВАНИЕ ДОКУМЕНТА ----------
  const handleDownloadDocument = () => {
    if (!documentData) return;

    setIsLoading(true);

    setTimeout(() => {
      const element = document.createElement("a");
      const file = new Blob([documentData.content], { type: "text/plain" });
      element.href = URL.createObjectURL(file);
      element.download = `${documentData.title.toLowerCase().replace(/\s+/g, "_")}.docx`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);

      setIsLoading(false);
    }, 1500);
  };


  const handleContinueEditing = () => {
    setIsChatEnded(false);
    setCurrentMessage("Хочу внести правки в документ");
  };

  const handleNewDocument = () => {
    navigate('/');
  };


  const formatTime = (date) => {
    return date.toLocaleTimeString("ru-RU", {
      hour: "2-digit",
      minute: "2-digit"
    });
  };


  // ========================================================
  // ===================== RENDER ===========================
  // ========================================================

  return (
    <div className="chat-page">
      <Navbar />

      <div className="chat-container">
        
        {/* HEADER */}
        <div className="chat-header">
          <div className="chat-info">
            <Button variant="text" onClick={() => navigate('/')} className="back-button">
              ← Назад к главной
            </Button>
            <h1>Диалог с AI-помощником</h1>
            <p>ID запроса: <span className="request-id">{requestId}</span></p>
          </div>

          <div className="chat-actions">
            <Button variant="secondary" onClick={() => navigate('/account')} size="small">
              📋 Мои документы
            </Button>
          </div>
        </div>


        {/* MESSAGES */}
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-chat">
              <div className="empty-icon">💬</div>
              <h3>Начинаем анализ вашей проблемы</h3>
              <p>AI-помощник подключается...</p>
              <LoadingSpinner size="medium" text="Подключение" />
            </div>
          ) : (
            <div className="messages-container">
              {messages.map(message => (
                <div
                  key={message.id}
                  className={`message ${message.sender === 'user' ? 'message-user' : 'message-ai'}`}
                >
                  <div className="message-avatar">
                    {message.sender === "user" ? "👤" : "🤖"}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{message.text}</div>
                    <div className="message-time">{formatTime(message.timestamp)}</div>
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
                        <span></span><span></span><span></span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>


        {/* DOCUMENT CARD */}
        {isChatEnded && documentData && (
          <div className="document-section">
            <div className="document-card">
              <div className="document-header">
                <div className="document-icon">🎉</div>
                <div className="document-info">
                  <h3>Ваш документ готов!</h3>
                  <p>{documentData.title}</p>
                </div>
              </div>

              <div className="document-details">
                <div className="detail-item">
                  <span className="label">Тип документа:</span>
                  <span className="value">{documentData.type}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Адресат:</span>
                  <span className="value">{documentData.recipient}</span>
                </div>
                <div className="detail-item">
                  <span className="label">Дата создания:</span>
                  <span className="value">{documentData.date}</span>
                </div>
              </div>

              <div className="document-actions">
                <Button 
                  variant="primary"
                  onClick={handleDownloadDocument}
                  loading={isLoading}
                >
                  📥 Скачать DOCX
                </Button>
                <Button variant="secondary" onClick={handleContinueEditing}>
                  ✏️ Продолжить редактирование
                </Button>
                <Button variant="text" onClick={() => navigate('/account')}>
                  💾 Сохранить в профиль
                </Button>
              </div>
            </div>
          </div>
        )}


        {/* INPUT FORM */}
        {!isChatEnded && (
          <form onSubmit={handleSendMessage} className="chat-input-form">
            <div className="input-container">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                placeholder="Введите ваш ответ..."
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

            <div className="input-hint">Нажмите Enter для отправки сообщения</div>
          </form>
        )}


        {/* QUICK ACTIONS */}
        {isChatEnded && (
          <div className="quick-actions">
            <div className="actions-title">Что дальше?</div>

            <div className="actions-grid">
              <div className="action-card" onClick={handleNewDocument}>
                <div className="action-icon">🆕</div>
                <h4>Новый документ</h4>
                <p>Создать новое обращение</p>
              </div>

              <div className="action-card" onClick={() => navigate('/account')}>
                <div className="action-icon">📋</div>
                <h4>Мои документы</h4>
                <p>Посмотреть историю</p>
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
