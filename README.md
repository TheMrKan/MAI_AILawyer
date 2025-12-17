# Claim-Composer AI
### Веб-сервис для составления юридически грамотных документов (обращений) в области трудового права через чат-бот на базе ИИ.

- #### RAG система с актуальной базой правовых актов.
- #### Проверенные шаблоны из официальных источников.
- #### Быстрый старт через Google.
- #### Не нужно составлять промпты - агент задаст все уточняющие вопросы.
- #### Корректное составление обращения в свободной форме в случае отсутствия шаблона.
- #### Экспорт файла в DOCX.
- #### Полностью бесплатный.

# Backend

## Что посмотреть
- В процессе получился неплохой самописный DI с авто-поиском сервисов; Transient, Scoped и Singleton; настраиваемым порядком загрузки. Не хотелось привязываться к FastAPI. Также нужно прокидывать зависимости в ноды.<br>
  [Ссылка на DI](https://github.com/TheMrKan/MAI_AILawyer/blob/master/backend/src/application/provider.py)
- Основные эндпоинты: создание обращения, добавление сообщения. Остальные, скажем так, второстепенные.<br>
  [Ссылка на эндпоинты](https://github.com/TheMrKan/MAI_AILawyer/blob/master/backend/src/api/issue.py)
- Всё что связано с графом LLM агента. По факту - это и есть бизнес-логика. Получилось неплохо оторвать её от любых реализаций (кроме самого langgraph конечно).<br>
  [Ссылка на граф](https://github.com/TheMrKan/MAI_AILawyer/blob/master/backend/src/core/chats/)

## Информация
### Архитектура
- `src.api` - слой представления. Принимает/возвращает свои схемы, а не внутренние DTO. 
  Преимущественно работает с сервисами через интефейсы (абстрактные классы).
- `src.application` - системы, необходимые для работы приложения. Лежат между слоем представления и основной логикой.
- `src.core` - ключевые компоненты приложения. Внутри была попытка сделать "кричащую" архитектуру, поэтому поделено не по слоям, а, скажем так, по доменам. 
  В файлах `types` находятся DTO. Ими общаются между собой все компоненты даже в других слоях. В `iface` находятся интерфейсы (абстрактные классы в нашем случае).
  Ядро определяет контракты репозиториев, которые ему нужны, а реализации подстраиваются под них. 
  Для некоторых сервисов нет интерфейсов и они используются напрямую (хотя объект всё еще берется из DI). Это осознанное решение, т. к. представить себе несколько реализаций этих сервисов очень сложно.
  По факту такие сервисы могли быть заменены обычными функциями. 
- `src.storage` - слой хранения данных. В нем находится большинство реализаций всех интерфейсов из `core`.
- `src.external` - коннекторы для внешних сервисов. Находятся на одном уровне с `storage`.

### Шаблоны
На данном этапе шаблоны хранятся в файловой системе в формате DOCX.<br>
Используется язык шаблонов Jinja: `{{variable}}`.<br>
Метаданные шаблонов с инструкциями для агента хранятся в Chroma. 

### Дисклеймер
Работу с пользователями и авторизацией писал Николай. 
Это его первый опыт с FastAPI, БД и фреймворками в целом, поэтому прошу понять и простить некоторые огрехи.
Мне тоже больно смотреть на некоторые вещи, но всё самое проблемное уже исправлено.

### Документация 
Основная документация находится в Сфере. Не вижу смысла дублировать её целиком в README.
#### Интерактивная документация по API сделана через Swagger. Она есть! `/docs/`


## Структура
```
.
├── src
│   ├── api
│   │   ├── auth.py    # эндпоинты авторизации
│   │   ├── deps.py    # Depends зависимости для эндпоинтов
│   │   ├── issue.py    # основные эндпоинты для работы с обращениями
│   │   ├── laws.py    # служебные эндпоинты для управления базой правовых актов
│   │   └── profile.py    # эндпоинты профиля
│   ├── application
│   │   ├── logging.py    # логгирование
│   │   └── provider.py    # самописный Dependency Injection
│   ├── config.py
│   ├── core    # не чистая бизнес-логика, но ключевой функционал приложения
│   │   ├── chats
│   │   │   ├── graph    # граф LLM агента
│   │   │   │   ├── common.py    # общие утилиты/классы
│   │   │   │   ├── free_template_subgraph.py    # подграф обращения в свободной форме
│   │   │   │   ├── full_chat_graph.py    # общий граф, объединяющий все подграфы
│   │   │   │   ├── laws_analysis_subgraph.py    # подграф анализа найденных правовых актов
│   │   │   │   ├── strict_template_subgraph.py    # подграф обращения в строгой форме
│   │   │   │   └── template_analysis_subgraph.py    # подграф анализа найденного шаблона
│   │   │   ├── service.py    # сервис для управления чатами
│   │   │   └── types.py    # DTO чатов
│   │   ├── issue_service.py    # сервис управления обращениями
│   │   ├── laws
│   │   │   ├── iface.py    # интерфейсы для правовых актов
│   │   │   └── types.py    # DTO правовых актов
│   │   ├── llm
│   │   │   ├── iface.py    # интерфейсы для LLM
│   │   │   └── use_cases.py    # сценарии использования LLM с промптами
│   │   ├── results
│   │   │   └── iface.py    # интерфейсы для выходных файлов
│   │   ├── templates
│   │   │   ├── content_service.py    # сервис для работы с содержимым шаблонов
│   │   │   ├── iface.py     # интерфейсы шаблонов
│   │   │   ├── manager.py    # сервис для управления шаблонами
│   │   │   └── types.py    # DTO шаблонов
│   │   └── users
│   │       ├── auth_service.py    # сервис авторизации
│   │       ├── iface.py    # интерфейсы авторизации и управления пользователями
│   │       └── types.py    # DTO пользователей и авторизации
│   ├── exceptions.py    # общие исключения
│   ├── external
│   │   ├── cerebras_llm.py    # реализация LLMABC для Cerebras
│   │   └── google_oauth.py    # реализация OAuthProviderABC для Google OAuth
│   ├── main.py    # точка входа
│   └── storage
│       ├── chroma
│       │   ├── base_chroma_repository.py    # базовый класс для Chroma репозиториев
│       │   ├── chroma_law_docs_repo.py    # Chroma реализация репозитория правовых актов
│       │   ├── chroma_templates_repo.py    # Chroma реализация репозитория шаблонов
│       │   └── connection.py    # хранит объект подключения в Chroma
│       ├── filesystem
│       │   ├── fs_issue_result_storage.py    # реализация хранилища выходных файлов в файловой системе
│       │   └── fs_templates_storage.py    # реализация хранилища шаблонов в файловой системе
│       └── sql
│           ├── base.py    # базовый класс для моделей
│           ├── connection.py    # управление подключением к SQL-БД
│           ├── models.py    # модели БД
│           └── user_repository.py    # SQL реализация репозитория пользователей
├── tests
│   ├── api    # тесты эндпоинтов
│   │   ├── confest.py
│   │   ├── test_auth.py
│   │   ├── test_auth_integration.py
│   │   └── test_issue_integration.py
│   └── graph    # тесты графа LLM агента
│       ├── test_chat_graph_common.py
│       ├── test_full_chat_graph.py
│       ├── test_laws_analysis_subgraph.py
│       ├── test_free_template_subgraph.py
│       ├── test_strict_template_subgraph.py
│       └── test_template_analysis_subgraph.py
├── .dockerignore
├── .env
├── .gitattributes
├── .gitignore
├── Dockerfile
├── poetry.lock
├── pyproject.toml
└── requirements.txt    # чтобы не тащить uv/poetry в образ
```

## Конфигурация
Маунт директории шаблонов по умолчанию `/backend/templates/`<br>
Маунт директории выходных файлов по умолчанию `/backend/results/`

#### Переменные окружения:
```
GOOGLE_CLIENT_ID=<ID приложения для Google OAuth>
GOOGLE_CLIENT_SECRET=<Секретный ключ для Google OAuth>
SECRET_KEY=<произвольный секретный ключ для генерации JWT>
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/postgres
ACCESS_TOKEN_EXPIRE_MINUTES=<время жизни авторизации в минутах>
YC_AUTH_TOKEN=<Yandex Cloud API KEY>
YC_FOLDER=<Yandex Cloud Folder ID>
POSTGRES_DB=<PostgreSQL DB Name>
POSTGRES_USER=<PostgreSQL username>
POSTGRES_PASSWORD=<PostgreSQL password>
TEMPLATES_DIR=/app/templates    # можно изменить директорию шаблонов внутри контейнера
RESULTS_DIR=/app/results    # можно изменить директорию выходных файлов внутри контейнера
BACKEND_URL=http://localhost:8000    # базовый URL бэкенда. Используется для callback url в SSO
FRONTEND_URL=http://localhost:5173    # базовый URL фронтенда. Используется для redirect url в SSO
```

# Установка, запуск (для разработки)
Клонируем репозиторий
```shell
git clone https://github.com/TheMrKan/MAI_AILawyer/
cd MAI_AILawyer
```

Настраиваем `.env` как описано выше. Некоторые переменные уже заданы в `docker-compose.dev.yaml`.

Поднимаем сервисы:
```shell
docker compose -f docker-compose.dev.yaml up 
```
Запустятся бэкенд, Chroma, PostgreSQL и фронтенд.
По умолчанию при разработке фронтенд доступен по адресу:
### [http://localhost:5173/]()

