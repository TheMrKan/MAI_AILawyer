import React from 'react';
import './DocumentCard.scss';

const DocumentCard = ({ document, onDownload, onView, onContinue }) => {
  const getStatusConfig = (status) => {
    const config = {
      completed: { label: 'Завершено', class: 'completed', icon: '✅' },
      draft: { label: 'Черновик', class: 'draft', icon: '📝' },
      processing: { label: 'В обработке', class: 'processing', icon: '⏳' }
    };
    return config[status] || config.draft;
  };

  const statusConfig = getStatusConfig(document.status);

  return (
    <div className={`document-card ${statusConfig.class}`}>
      <div className="document-header">
        <div className="document-title-section">
          <h3 className="document-title">{document.title}</h3>
          <span className={`document-status ${statusConfig.class}`}>
            {statusConfig.icon} {statusConfig.label}
          </span>
        </div>
        <div className="document-date">
          {new Date(document.createdAt).toLocaleDateString('ru-RU')}
        </div>
      </div>

      <div className="document-info">
        <div className="info-row">
          <span className="info-label">Тип документа:</span>
          <span className="info-value">{document.type}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Адресат:</span>
          <span className="info-value">{document.recipient}</span>
        </div>
        {document.description && (
          <div className="document-description">
            {document.description}
          </div>
        )}
      </div>

      <div className="document-actions">
        {document.status === 'completed' ? (
          <>
            <button 
              className="btn-primary btn-small"
              onClick={() => onDownload(document.id)}
            >
              📥 Скачать DOCX
            </button>
            <button 
              className="btn-secondary btn-small"
              onClick={() => onView(document.id)}
            >
              👁️ Просмотреть
            </button>
          </>
        ) : (
          <button 
            className="btn-primary btn-small"
            onClick={() => onContinue(document.id)}
          >
            ✏️ Продолжить
          </button>
        )}
      </div>
    </div>
  );
};

export default DocumentCard;