import React from 'react';
import Navbar from '../../components/Navbar/Navbar';
import Footer from '../../components/Footer/Footer';
import Button from '../../components/Button/Button';
import './AboutPage.scss';

const AboutPage = () => {
  const teamMembers = [
    {
      name: 'Кудратов Навруз',
      role: 'Frontend Developer & Designer',
      bio: 'Разработка пользовательского интерфейса, дизайн системы',
      avatar: '🎨',
      skills: ['React', 'UI/UX Design', 'SCSS']
    },
    {
      name: 'Эль-Тахир Роман',
      role: 'Team Lead & Designer',
      bio: 'Руководство проектом, архитектура системы, дизайн',
      avatar: '👨‍💼',
      skills: ['Project Management', 'System Architecture', 'Design']
    },
    {
      name: 'Кандрушин Егор',
      role: 'Backend Developer (LLM)',
      bio: 'Разработка AI-моделей и интеграция языковых моделей',
      avatar: '🤖',
      skills: ['Python', 'LLM', 'AI Integration']
    },
    {
      name: 'Сугай Вячеслав',
      role: 'Backend Developer',
      bio: 'Разработка серверной части и бизнес-логики',
      avatar: '⚙️',
      skills: ['Python', 'Backend', 'API Development']
    },
    {
      name: 'Лазаревич Николай',
      role: 'Backend Developer (FastAPI)',
      bio: 'Разработка API и серверной инфраструктуры',
      avatar: '🚀',
      skills: ['Python', 'FastAPI', 'Microservices']
    },
  ];

  return (
    <div className="about-page">
      <Navbar />
      
      <div className="about-container">
        {/* Hero Section */}
        <section className="about-hero">
          <div className="hero-content">
            <h1>О проекте Claim-Composer AI</h1>
            <p className="hero-subtitle">
              Демократизируем доступ к правовой защите с помощью искусственного интеллекта
            </p>
            
          </div>
        </section>

        {/* Mission Section */}
        <section className="mission-section">
          <div className="container">
            <h2>Наша миссия</h2>
            <div className="mission-content">
              <div className="mission-text">
                <p>
                  Мы создали Claim-Composer AI, чтобы каждый человек мог получить квалифицированную 
                  юридическую помощь независимо от своего дохода, образования или местоположения. 
                </p>
                <p>
                  Наша платформа использует передовые технологии искусственного интеллекта для 
                  автоматизации создания юридических документов, делая правовую защиту доступной 
                  для всех.
                </p>
                <div className="mission-values">
                  <div className="value-item">
                    <div className="value-icon">🎯</div>
                    <div className="value-content">
                      <h4>Доступность</h4>
                      <p>Помощь доступна каждому в любое время</p>
                    </div>
                  </div>
                  <div className="value-item">
                    <div className="value-icon">⚡</div>
                    <div className="value-content">
                      <h4>Скорость</h4>
                      <p>Документы создаются за минуты вместо часов</p>
                    </div>
                  </div>
                  <div className="value-item">
                    <div className="value-icon">🛡️</div>
                    <div className="value-content">
                      <h4>Надежность</h4>
                      <p>Все документы соответствуют законодательству</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mission-visual">
                <div className="visual-card">
                  <div className="card-icon">⚖️</div>
                  <h4>Юридическая экспертиза</h4>
                  <p>Автоматический анализ вашей ситуации</p>
                </div>
                <div className="visual-card">
                  <div className="card-icon">🤖</div>
                  <h4>AI технологии</h4>
                  <p>Современные алгоритмы машинного обучения</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section className="how-it-works-section">
          <div className="container">
            <h2>Как работает наш AI</h2>
            <div className="process-steps">
              <div className="process-step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h3>Анализ проблемы</h3>
                  <p>AI анализирует ваше описание и определяет суть проблемы</p>
                </div>
              </div>
              <div className="process-step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h3>Подбор законов</h3>
                  <p>Система находит подходящие нормативные акты</p>
                </div>
              </div>
              <div className="process-step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h3>Генерация документа</h3>
                  <p>Создается юридически грамотный документ</p>
                </div>
              </div>
              <div className="process-step">
                <div className="step-number">4</div>
                <div className="step-content">
                  <h3>Проверка качества</h3>
                  <p>Документ проверяется на соответствие требованиям</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Team Section */}
        <section className="team-section">
          <div className="container">
            <h2>Наша команда</h2>
            <p className="section-subtitle">
              Профессионалы в области разработки и искусственного интеллекта
            </p>
            <div className="team-grid">
              {teamMembers.map((member, index) => (
                <div key={index} className="team-card">
                  <div className="member-avatar">
                    {member.avatar}
                  </div>
                  <h3>{member.name}</h3>
                  <div className="member-role">{member.role}</div>
                  <p className="member-bio">{member.bio}</p>
                  <div className="member-skills">
                    {member.skills.map((skill, skillIndex) => (
                      <span key={skillIndex} className="skill-tag">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Tech Stack Section */}
        <section className="tech-stack-section">
          <div className="container">
            <h2>Технологический стек</h2>
            <div className="tech-grid">
              <div className="tech-category">
                <h3>Frontend</h3>
                <div className="tech-items">
                  <div className="tech-item">React 18</div>
                  <div className="tech-item">Vite</div>
                  <div className="tech-item">SCSS</div>
                  <div className="tech-item">React Router</div>
                </div>
              </div>
              <div className="tech-category">
                <h3>Backend</h3>
                <div className="tech-items">
                  <div className="tech-item">Python</div>
                  <div className="tech-item">FastAPI</div>
                  <div className="tech-item">LangGraph</div>
                  <div className="tech-item">Cerebras LLM</div>
                </div>
              </div>
              <div className="tech-category">
                <h3>Infrastructure</h3>
                <div className="tech-items">
                  <div className="tech-item">Docker</div>
                  <div className="tech-item">Docker Compose</div>
                  <div className="tech-item">Nginx</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        
        {/* CTA Section */}
        <section className="cta-section">
          <div className="container">
            <div className="cta-content">
              <h2>Готовы решить вашу проблему?</h2>
              <p>Начните прямо сейчас с создания вашего первого документа</p>
              <div className="cta-actions">
                <Button 
                  variant="primary" 
                  onClick={() => window.location.href = '/'}
                  size="large"
                >
                  Создать документ
                </Button>
              </div>
            </div>
          </div>
        </section>
      </div>

      <Footer />
    </div>
  );
};

export default AboutPage;