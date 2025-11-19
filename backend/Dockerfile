FROM python:3.12.10-slim AS deps
WORKDIR /app

RUN apt install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt ./
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install -r requirements.txt --no-cache-dir


COPY . .
WORKDIR /app/src

ENTRYPOINT ["fastapi", "run", "main.py"]



