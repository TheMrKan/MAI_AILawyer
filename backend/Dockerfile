### Слой зависимостей
FROM python:3.12.10-slim AS deps
WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt --no-cache-dir


### Слой кода приложения (для разработки)
FROM deps AS app_dev
WORKDIR /app
COPY . .
WORKDIR /app/src

ENTRYPOINT ["fastapi", "run", "main.py"]



