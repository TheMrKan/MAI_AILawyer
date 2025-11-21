import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import Modal from '../../components/Modal/Modal';
import './AccountPage.scss';

const AccountPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('documents');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Данные user
  const [userData, setUserData] = useState({
    name: 'Иван Иванов',
    email: 'ivan@example.com',
    phone: '+7 (999) 123-45-67',
    joinDate: '15 января 2024',
    avatar: '👤'
  });

  // Документы user .
  const [documents, setDocuments] = useState([
    {
      id: 1,
      title: 'Претензия о возврате денежных средств',
      date: '2024-01-15',
      status: 'completed',
      type: 'Жалоба',
      recipient: 'Магазин "Электроник"',
      downloadUrl: '#'
    },
    {
      id: 2,
      title: 'Заявление в Роспотребнадзор',
      date: '2024-01-10',
      status: 'completed',
      type: 'Заявление',
      recipient: 'Роспотребнадзор',
      downloadUrl: '#'
    },
    {
      id: 3,
      title: 'Жалоба на действия банка',
      date: '2024-01-05',
      status: 'draft',
      type: 'Жалоба',
      recipient: 'Банк "Финансовый"',
      downloadUrl: '#'
    },
    {
      id: 4,
      title: 'Исковое заявление в суд',
      date: '2024-01-01',
      status: 'processing',
      type: 'Исковое заявление',
      recipient: 'Мировой суд',
      downloadUrl: '#'
    }
  ]);

  // Статистика
  const stats = {
    totalDocuments: documents.length,
    completed: documents.filter(d => d.status === 'completed').length,
    drafts: documents.filter(d => d.status === 'draft').length,
    inProgress: documents.filter(d => d.status === 'processing').length
  };

  const handleDownload = (documentId) => {
    setIsLoading(true);
    // пасс
    setTimeout(() => {
      alert(`Документ ${documentId} скачивается...`);
      setIsLoading(false);
    }, 1000);
  };

  const handleContinue = (documentId) => {
    navigate(`/chat/${documentId}`);
  };

  const handleEditProfile = () => {
    setIsEditModalOpen(true);
  };

  const handleSaveProfile = (updatedData) => {
    setUserData(updatedData);
    setIsEditModalOpen(false);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      completed: { text: 'Завершено', class: 'status-completed', icon: '✅' },
      draft: { text: 'Черновик', class: 'status-draft', icon: '📝' },
      processing: { text: 'В обработке', class: 'status-processing', icon: '⏳' }
    };
    
    const config = statusConfig[status] || statusConfig.draft;
    return (
      <span className={`status-badge ${config.class}`}>
        <span className="status-icon">{config.icon}</span>
        {config.text}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="account-page">
        <Navbar />
        <div className="loading-container">
          <LoadingSpinner size="large" text="Загрузка данных..." />
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="account-page">
      <Navbar />
      
      <div className="account-container">
        {/* Хедер профиля */}
        <div className="profile-header">
          <div className="profile-avatar">
            <div className="avatar-circle">
              {userData.avatar}
            </div>
            <div className="profile-info">
              <h1>{userData.name}</h1>
              <p>Участник с {userData.joinDate}</p>
              <div className="profile-contacts">
                <span className="contact-item">📧 {userData.email}</span>
                <span className="contact-item">📞 {userData.phone}</span>
              </div>
            </div>
          </div>
          <Button 
            variant="secondary" 
            onClick={handleEditProfile}
            className="edit-profile-btn"
          >
            ✏️ Редактировать профиль
          </Button>
        </div>

        {/* Статистика */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📄</div>
            <div className="stat-content">
              <div className="stat-number">{stats.totalDocuments}</div>
              <div className="stat-label">Всего документов</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <div className="stat-number">{stats.completed}</div>
              <div className="stat-label">Завершено</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">📝</div>
            <div className="stat-content">
              <div className="stat-number">{stats.drafts}</div>
              <div className="stat-label">Черновики</div>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">⏳</div>
            <div className="stat-content">
              <div className="stat-number">{stats.inProgress}</div>
              <div className="stat-label">В работе</div>
            </div>
          </div>
        </div>

        {/* Навигация по табам */}
        <div className="tabs-navigation">
          <button 
            className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            📋 Мои документы
          </button>
          <button 
            className={`tab-btn ${activeTab === 'activity' ? 'active' : ''}`}
            onClick={() => setActiveTab('activity')}
          >
            📊 Активность
          </button>
          <button 
            className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            ⚙️ Настройки
          </button>
        </div>

        {/* Контент табов */}
        <div className="tab-content">
          {activeTab === 'documents' && (
            <div className="documents-section">
              <div className="section-header">
                <h2>Мои документы</h2>
                <Button 
                  onClick={() => navigate('/')}
                  className="create-new-btn"
                >
                  ➕ Создать новый
                </Button>
              </div>

              
            </div>
          )}

          
          {activeTab === 'settings' && (
            <div className="settings-section">
              <h2>Настройки аккаунта</h2>
              <div className="settings-grid">
                <div className="setting-item">
                  <h3>Уведомления</h3>
                  <p>Настройте получение уведомлений о статусе документов</p>
                  <Button variant="secondary" size="small">
                    Настроить
                  </Button>
                </div>
                <div className="setting-item">
                  <h3>Безопасность</h3>
                  <p>Измените пароль и настройки безопасности</p>
                  <Button variant="secondary" size="small">
                    Обновить
                  </Button>
                </div>
                <div className="setting-item">
                  <h3>Экспорт данных</h3>
                  <p>Скачайте все ваши документы и данные</p>
                  <Button variant="secondary" size="small">
                    Экспортировать
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      <Footer />

      {/* Модальное окно редактирования профиля */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Редактирование профиля"
        size="medium"
      >
        <EditProfileForm 
          userData={userData}
          onSave={handleSaveProfile}
          onCancel={() => setIsEditModalOpen(false)}
        />
      </Modal>
    </div>
  );
};


const EditProfileForm = ({ userData, onSave, onCancel }) => {
  const [formData, setFormData] = useState(userData);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="edit-profile-form">
      <div className="form-group">
        <label>Имя и фамилия</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="Введите ваше имя"
        />
      </div>
      
      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          placeholder="Введите ваш email"
        />
      </div>
      
      <div className="form-group">
        <label>Телефон</label>
        <input
          type="tel"
          value={formData.phone}
          onChange={(e) => handleChange('phone', e.target.value)}
          placeholder="Введите ваш телефон"
        />
      </div>

      <div className="form-actions">
        <Button type="button" variant="text" onClick={onCancel}>
          Отмена
        </Button>
        <Button type="submit" variant="primary">
          Сохранить изменения
        </Button>
      </div>
    </form>
  );
};

export default AccountPage;