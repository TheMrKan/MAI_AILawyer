# ----------------------------
# Стадия разработки (dev)
# ----------------------------
FROM node:20-alpine AS development

# Устанавливаем необходимые пакеты для сборки
RUN apk add --no-cache bash git python3 make g++

WORKDIR /app

# Копируем package files для установки зависимостей
COPY package*.json ./

# Чистая установка зависимостей
RUN npm ci

# Копируем весь исходный код
COPY . .

# Переменная окружения для dev
ENV VITE_API_URL=http://backend:8000

# Экспонируем порт dev-сервера Vite
EXPOSE 5173

# Запуск dev-сервера Vite
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ----------------------------
# Стадия сборки (builder)
# ----------------------------
FROM node:20-alpine AS builder

RUN apk add --no-cache bash git python3 make g++

WORKDIR /app

# Копируем только package.json и package-lock.json для кэширования
COPY package*.json ./

# Чистая установка зависимостей
RUN npm ci

# Копируем весь исходный код
COPY . .

# Сборка фронтенда
RUN npm run build

# ----------------------------
# Стадия продакшена (nginx)
# ----------------------------
FROM nginx:alpine AS production

# Копируем билд фронтенда
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем конфиг Nginx, если есть
# Если конфигурация стандартная, эту строку можно удалить
COPY nginx.conf /etc/nginx/nginx.conf

# Экспонируем стандартный HTTP порт
EXPOSE 80

# Запуск Nginx в форграунд-режиме
CMD ["nginx", "-g", "daemon off;"]
