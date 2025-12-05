FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    netcat-traditional \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Создание директорий для загрузок
RUN mkdir -p /app/uploads/avatars /app/uploads/posts /app/uploads/chat
RUN chmod -R 755 /app/uploads

# Копирование дефолтного аватара
COPY app/static/uploads/avatars/default-avatar.png /app/uploads/avatars/

# Права на выполнение для entrypoint
RUN chmod +x /app/entrypoint.sh

# Открываем порт
EXPOSE 5000

# Точка входа
ENTRYPOINT ["/app/entrypoint.sh"]

