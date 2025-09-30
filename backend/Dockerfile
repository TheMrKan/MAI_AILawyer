### Слой зависимостей
FROM python:3.12.10-slim AS deps
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential

RUN pip install poetry --no-cache-dir
COPY pyproject.toml poetry.lock ./

# ставим только продовые зависимости без создания окружения
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root


### Слой кода приложения (для разработки)
FROM deps AS app_dev
WORKDIR /app
COPY . .
WORKDIR /app/src

ENTRYPOINT ["fastapi", "run", "main.py"]



