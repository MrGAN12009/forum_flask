# Быстрый старт

Минимальная инструкция для запуска форума за 5 минут.

## Требования

- Docker
- Docker Compose

## Установка и запуск

### 1. Создайте дефолтный аватар

```bash
python create_default_avatar.py
```

Или скачайте любую картинку 200x200px и сохраните как `app/static/uploads/avatars/default-avatar.png`

### 2. Настройте окружение

Скопируйте `.env.example`:
```bash
# Linux/Mac
cp .env.example .env

# Windows
copy .env.example .env
```

Отредактируйте `.env` и установите `SECRET_KEY`:
```bash
# Сгенерируйте ключ
python -c "import secrets; print(secrets.token_hex(32))"

# Вставьте в .env
SECRET_KEY=ваш_сгенерированный_ключ
```

### 3. Запустите Docker

```bash
docker-compose up -d
```

### 4. Дождитесь инициализации

Проверьте логи:
```bash
docker-compose logs -f web
```

Дождитесь сообщения "Running database migrations..."

### 5. (Опционально) Добавьте тестовые данные

```bash
docker-compose exec web python scripts/init_db.py
```

### 6. Откройте браузер

Перейдите на http://localhost

## Тестовые пользователи

После выполнения шага 5:
- Email: `user1@example.com` / Пароль: `password123`
- Email: `user2@example.com` / Пароль: `password123`
- Email: `user3@example.com` / Пароль: `password123`

## Использование Makefile (опционально)

Если у вас установлен `make`:

```bash
# Полная автоматическая настройка
make setup

# Просмотр всех команд
make help

# Логи
make logs

# Перезапуск
make restart

# Остановка
make down
```

## Решение проблем

### Ошибка "Cannot connect to database"

Подождите еще немного - БД может инициализироваться. Проверьте:
```bash
docker-compose ps
```

Все сервисы должны быть в статусе "Up".

### Порт 80 занят

Измените порты в `docker-compose.yml`:
```yaml
nginx:
  ports:
    - "8080:80"  # Вместо "80:80"
```

Затем открывайте http://localhost:8080

### Ошибка "default-avatar.png not found"

Создайте файл:
```bash
python create_default_avatar.py
```

Или скачайте любую картинку и сохраните как `app/static/uploads/avatars/default-avatar.png`

## Следующие шаги

- Зарегистрируйте свой аккаунт
- Создайте первый топик
- Попробуйте чат между пользователями
- Настройте HTTPS (см. README.md)

## Остановка

```bash
docker-compose down
```

Для полной очистки (удаляет БД):
```bash
docker-compose down -v
```

