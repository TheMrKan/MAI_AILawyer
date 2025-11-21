## UPDATE
Смотрите репозиторий этой версии: https://github.com/TheMrKan/MAI_AILawyer/tree/ea43d56f50370d9a02fa9fb00f78609885626487

## Сборка
Путь до Dockerfile: ./backend/Dockerfile

Размер образа <500 MB невозможен, т. к. только зависимости занимают 450+ MB. 

## Переменные окружения
- `CEREBRAS_API_KEY` - API ключ для Cerebras LLM (запустится с любым).
- `TEMPLATES_DIR` - путь до директории внутри контейнера, в которой хранятся файлы шаблонов.

## Сервисы
**Ожидает доступную ChromaDB по адресу `http://chroma:8000/`**.<br>
**Без ChromaDB приложение не запустится!**

## Запуск
Команда для запуска с маунтом для разработки.<br>
`docker run -v "$(pwd)/backend/src/:/app/src/" -p 8000:8000 mrkan0/ai-lawyer-backend`

Рекомендуется использовать `docker-compose.dev.yaml` для запуска.
