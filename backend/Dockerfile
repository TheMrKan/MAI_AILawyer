FROM python:3.12.10-slim AS build
WORKDIR /app

RUN apt update && apt install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY poetry.lock .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    pip uninstall poetry -y


FROM python:3.12.10-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1

RUN useradd -m appuser
USER appuser

COPY --from=build /usr/local /usr/local

COPY --chown=appuser:appuser . .

WORKDIR /app/src

ENTRYPOINT ["fastapi", "run", "main.py"]





