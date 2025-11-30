import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import Modal from '../../components/Modal/Modal';
import { userAPI } from '../../services/api';
import './AccountPage.scss';

const AccountPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('documents');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Данные пользователя
  const [userData, setUserData] = useState(null);
  const [documents, setDocuments] = useState([]);

  // Загружаем данные пользователя
  useEffect(() => {
    const loadUserData = async () => {
      try {
        const user = localStorage.getItem('user');
        if (user) {
          setUserData(JSON.parse(user));
        }

        // Здесь можно добавить загрузку документов с API
        // const docs = await userAPI.getDocuments();
        // setDocuments(docs);

      } catch (error) {
        console.error('Error loading user data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadUserData();
  }, []);

  const handleSaveProfile = async (updatedData) => {
    try {
      // await userAPI.updateProfile(updatedData);
      setUserData(updatedData);
      localStorage.setItem('user', JSON.stringify(updatedData));
      setIsEditModalOpen(false);
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Ошибка при обновлении профиля');
    }
  };

  const handleDownload = (documentId) => {
    setIsLoading(true);
    // Заглушка для скачивания
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
              {userData?.avatar || '👤'}
            </div>
            <div className="profile-info">
              <h1>{userData?.name || 'Пользователь'}</h1>
              <p>Участник с {userData?.joinDate || 'недавно'}</p>
              <div className="profile-contacts">
                <span className="contact-item">📧 {userData?.email || 'email@example.com'}</span>
                <span className="contact-item">📞 {userData?.phone || '+7 (999) 999-99-99'}</span>
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

              <div className="documents-grid">
                {documents.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">📄</div>
                    <h3>У вас пока нет документов</h3>
                    <p>Создайте свой первый документ, чтобы начать работу</p>
                    <Button onClick={() => navigate('/')}>
                      Создать документ
                    </Button>
                  </div>
                ) : (
                  documents.map(doc => (
                    <div key={doc.id} className="document-card">
                      <div className="document-header">
                        <h3>{doc.title}</h3>
                        {getStatusBadge(doc.status)}
                      </div>
                      <div className="document-info">
                        <div className="info-item">
                          <span className="label">Тип:</span>
                          <span className="value">{doc.type}</span>
                        </div>
                        <div className="info-item">
                          <span className="label">Получатель:</span>
                          <span className="value">{doc.recipient}</span>
                        </div>
                        <div className="info-item">
                          <span className="label">Дата создания:</span>
                          <span className="value">{doc.date}</span>
                        </div>
                      </div>
                      <div className="document-actions">
                        <Button
                          size="small"
                          onClick={() => handleDownload(doc.id)}
                        >
                          📥 Скачать
                        </Button>
                        {doc.status === 'draft' && (
                          <Button
                            variant="secondary"
                            size="small"
                            onClick={() => handleContinue(doc.id)}
                          >
                            ➕ Продолжить
                          </Button>
                        )}
                      </div>
                    </div>
                  ))
                )}
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

// Компонент формы редактирования профиля
const EditProfileForm = ({ userData, onSave, onCancel }) => {
  const [formData, setFormData] = useState(userData || {});

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
          value={formData.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="Введите ваше имя"
        />
      </div>

      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={formData.email || ''}
          onChange={(e) => handleChange('email', e.target.value)}
          placeholder="Введите ваш email"
        />
      </div>

      <div className="form-group">
        <label>Телефон</label>
        <input
          type="tel"
          value={formData.phone || ''}
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