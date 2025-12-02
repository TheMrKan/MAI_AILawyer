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
        const parsedUser = JSON.parse(user);
        console.log('Loaded user from localStorage:', parsedUser); // Добавим для отладки

        // Проверяем, есть ли данные из Google
        if (parsedUser.id) {
          setUserData(parsedUser);

          // Если имя пустое или дефолтное, пробуем взять из email
          if (!parsedUser.name || parsedUser.name === 'Пользователь' || parsedUser.name === parsedUser.email) {
            const nameFromEmail = parsedUser.email?.split('@')[0] || 'Пользователь';
            const updatedUser = {
              ...parsedUser,
              name: nameFromEmail
            };
            setUserData(updatedUser);
            localStorage.setItem('user', JSON.stringify(updatedUser));
          }
        } else {
          // Если данных нет, перенаправляем на авторизацию
          navigate('/signin');
        }
      } else {
        // Если пользователя нет в localStorage, перенаправляем на авторизацию
        navigate('/signin');
      }

      // Здесь можно добавить загрузку документов с API
      // const docs = await userAPI.getDocuments();
      // setDocuments(docs);

    } catch (error) {
      console.error('Error loading user data:', error);
      // В случае ошибки перенаправляем на авторизацию
      navigate('/signin');
    } finally {
      setIsLoading(false);
    }
  };

  loadUserData();
}, [navigate]);

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
              {userData?.avatar ? (
                <img
                  src={userData.avatar}
                  alt="Аватар"
                  style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.style.display = 'none';
                    e.target.parentElement.textContent = userData?.name?.charAt(0) || '👤';
                  }}
                />
              ) : (
                userData?.name?.charAt(0) || '👤'
              )}
            </div>
            <div className="profile-info">
              {/* ДОБАВЬТЕ ЭТОТ ЗАГОЛОВОК h1 */}
              <h1>{userData?.name || 'Пользователь'}</h1>
              <p>{userData?.email || 'email@example.com'}</p>
              <div className="profile-contacts">
                <span className="contact-item">📧 {userData?.email || 'email@example.com'}</span>
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
  const [formData, setFormData] = useState(() => {
    // Инициализируем форму данными из Google
    const initialData = {
      name: userData?.name || '',
      email: userData?.email || '',
      phone: userData?.phone || '',
      firstName: userData?.firstName || userData?.name?.split(' ')[0] || '',
      lastName: userData?.lastName || userData?.name?.split(' ').slice(1).join(' ') || ''
    };

    console.log('Form initialized with:', initialData); // Для отладки
    return initialData;
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    // Обновляем данные пользователя
    const updatedData = {
      ...userData,
      ...formData,
      // Если имя было изменено, обновляем его
      name: formData.name || `${formData.firstName} ${formData.lastName}`.trim() || userData?.email?.split('@')[0],
      firstName: formData.firstName,
      lastName: formData.lastName,
      phone: formData.phone
    };

    console.log('Saving user data:', updatedData); // Для отладки
    onSave(updatedData);
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
        <label>Имя</label>
        <input
          type="text"
          value={formData.firstName || ''}
          onChange={(e) => handleChange('firstName', e.target.value)}
          placeholder="Введите ваше имя"
        />
      </div>

      <div className="form-group">
        <label>Фамилия</label>
        <input
          type="text"
          value={formData.lastName || ''}
          onChange={(e) => handleChange('lastName', e.target.value)}
          placeholder="Введите вашу фамилию"
        />
      </div>

      <div className="form-group">
        <label>Отображаемое имя</label>
        <input
          type="text"
          value={formData.name || ''}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="Имя для отображения"
        />
      </div>

      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={formData.email || ''}
          readOnly
          disabled
          className="disabled-input"
        />
        <small style={{ color: '#666', fontSize: '0.8rem' }}>
          Email изменить нельзя, так как используется для авторизации через Google
        </small>
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