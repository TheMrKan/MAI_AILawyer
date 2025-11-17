FROM python:3.12.10-slim AS deps
WORKDIR /app

COPY requirements.txt ./
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
WORKDIR /app/src

ENTRYPOINT ["fastapi", "run", "main.py"]

