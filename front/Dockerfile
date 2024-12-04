# Используем Node.js для разработки
FROM node:18

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm install

# Открываем порт для Vite
EXPOSE 5173

# Запускаем Vite в режиме watch
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
