# Указываем точную версию Node.js из .env
ARG NODE_VERSION=22.14.0
FROM node:${NODE_VERSION}-alpine

WORKDIR /src

# Кэшируем зависимости для ускорения сборки
COPY package.json package-lock.json ./
RUN npm install --frozen-lockfile

# Копируем остальные файлы
COPY . .

# Сборка проекта (если нужно)
RUN npm run build

# Запуск сервера
CMD ["npm", "start"]