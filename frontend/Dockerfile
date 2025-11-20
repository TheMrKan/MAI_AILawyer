# Стадия для разработки
FROM node:22-alpine AS development

WORKDIR /app

# Копируем package files
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]