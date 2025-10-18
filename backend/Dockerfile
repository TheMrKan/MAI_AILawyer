### Слой зависимостей
FROM python:3.12.10-slim AS deps
WORKDIR /app

RUN apt update && apt install -y --no-install-recommends build-essential \
    && apt-get clean # удаляет кэш списка пакетов из apt update \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*    # удаляет кэши пакетов после apt install

RUN pip install poetry --no-cache-dir
COPY pyproject.toml poetry.lock ./

# ставим только продовые зависимости без создания окружения
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main --no-root --no-cache


### Слой кода приложения (для разработки)
FROM deps AS app_dev
WORKDIR /app
COPY . .
WORKDIR /app/src

ENTRYPOINT ["fastapi", "run", "main.py"]



