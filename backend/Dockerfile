FROM python:3.12.10-slim AS deps
WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt --no-cache-dir

WORKDIR /app
COPY . .
WORKDIR /app/src

ENTRYPOINT ["fastapi", "run", "main.py"]

