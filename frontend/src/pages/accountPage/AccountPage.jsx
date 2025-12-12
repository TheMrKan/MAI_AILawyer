import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import LoadingSpinner from '../../components/LoadingSpinner/LoadingSpinner';
import Modal from '../../components/Modal/Modal';
import { userAPI, issueAPI } from '../../services/api';
import { motion, AnimatePresence } from "framer-motion";
import './AccountPage.scss';

const AccountPage = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('documents');
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [downloadingId, setDownloadingId] = useState(null);

  // Данные пользователя
  const [userData, setUserData] = useState(null);
  const [documents, setDocuments] = useState([]);

useEffect(() => {
  const loadDocuments = async () => {
    try {
      const docs = await userAPI.getUserDocuments();
      setDocuments(docs);
    } finally {
      setLoadingDocuments(false);
    }
  };

  loadDocuments();
}, []);

  // Загружаем данные пользователя
useEffect(() => {
      const loadUserData = async () => {
        try {
          const user = await userAPI.getMe();

          // нормализация данных
          const normalized = {
            id: user.id,
            email: user.email,
            name: `${user.first_name || ''} ${user.last_name || ''}`.trim()
              || user.email.split('@')[0],
            avatar: user.avatar_url,
            firstName: user.first_name,
            lastName: user.last_name,
            joinDate: user.created_at,
            phone: user.phone ?? '',
          };

          setUserData(normalized);
          localStorage.setItem('user', JSON.stringify(normalized));

        } catch (error) {
          console.error("Error loading user profile:", error);
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

  const handleDownload = async (issueId) => {
      try {
        setDownloadingId(issueId);

        const response = await issueAPI.downloadDocument(issueId);

        const blob = new Blob([response.data], {
          type:
            response.headers['content-type'] ||
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        });

        const url = window.URL.createObjectURL(blob);

        const link = document.createElement('a');
        link.href = url;
        link.download = `document_${issueId}.docx`;

        document.body.appendChild(link);
        link.click();

        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Download failed:', error);
        alert(error.message || 'Не удалось скачать документ');
      } finally {
        setDownloadingId(null);
      }
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
              <h1>{userData?.name || 'Пользователь'}</h1>
              <p>{userData?.email || 'email@example.com'}</p>
              <div className="profile-contacts">
                <span className="contact-item">📧 {userData?.email || 'email@example.com'}</span>
              </div>
            </div>
          </div>
        </div>


        {/* Контент табов */}
        <div className="tab-content">
          <AnimatePresence mode="wait">
            {activeTab === 'documents' && (
              <motion.div
                key="documents"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
                className="documents-section"
              >
                <div className="section-header">
                  <h2>Мои документы</h2>
                  <Button onClick={() => navigate('/')} className="create-new-btn">
                    ➕ Создать новый
                  </Button>
                </div>

                <div className="documents-grid">
                  {loadingDocuments ? (
                    [...Array(4)].map((_, i) => (
                      <div key={i} className="document-card skeleton">
                        <div className="skeleton-title" />
                        <div className="skeleton-line short" />
                        <div className="skeleton-line long" />
                        <div className="skeleton-footer" />
                      </div>
                    ))
                  ) : (
                    documents.map(doc => (
                      <div key={doc.id} className="document-card modern">

                        <div className="doc-top">
                          <h3 className="doc-title">{doc.title}</h3>
                          {getStatusBadge(doc.status)}
                        </div>

                        <p className="chatgpt-preview">{doc.text_preview}</p>

                        <div className="doc-footer">
                          <div className="doc-date">📅 {doc.date}</div>

                          <div className="doc-actions">
                            {doc.status === "completed" && (
                              <Button
                                  size="small"
                                  onClick={() => handleDownload(doc.id)}
                                  disabled={downloadingId === doc.id}
                                >
                                  {downloadingId === doc.id ? '⏳ Загрузка...' : '📥 Скачать'}
                              </Button>

                            )}

                            {doc.status === "draft" && (
                              <Button size="small" variant="secondary" onClick={() => handleContinue(doc.id)}>
                                ➕ Продолжить
                              </Button>
                            )}

                            {doc.status === "error" && (
                              <span className="doc-error">⚠ Ошибка</span>
                            )}
                          </div>
                        </div>

                      </div>
                    ))
                  )}
                </div>
              </motion.div>
            )}

            {activeTab === 'settings' && (
              <motion.div
                key="settings"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
                className="settings-section"
              >
                <h2>Настройки аккаунта</h2>

                <div className="settings-grid">
                  <div className="setting-item">
                    <h3>Уведомления</h3>
                    <p>Настройка уведомлений и уведомлений на email.</p>
                  </div>

                  <div className="setting-item">
                    <h3>Безопасность</h3>
                    <p>Изменить пароль или просмотреть активные устройства.</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
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