# Структура проекта

Полная структура файлов и директорий проекта форума.

```
forum/
│
├── app/                              # Главное приложение Flask
│   ├── __init__.py                   # Инициализация приложения, создание расширений
│   ├── models.py                     # Модели SQLAlchemy (User, Topic, Post, ChatMessage)
│   ├── utils.py                      # Вспомогательные функции (загрузка файлов и т.д.)
│   │
│   ├── auth/                         # Blueprint для аутентификации
│   │   ├── __init__.py
│   │   └── routes.py                 # Регистрация, вход, выход
│   │
│   ├── forum/                        # Blueprint для форума
│   │   ├── __init__.py
│   │   └── routes.py                 # Топики, посты, создание, удаление
│   │
│   ├── chat/                         # Blueprint для чата
│   │   ├── __init__.py
│   │   ├── routes.py                 # HTTP маршруты чата
│   │   └── events.py                 # WebSocket обработчики (SocketIO)
│   │
│   ├── profile/                      # Blueprint для профилей
│   │   ├── __init__.py
│   │   └── routes.py                 # Просмотр, редактирование профиля
│   │
│   ├── main/                         # Blueprint для главных страниц
│   │   ├── __init__.py
│   │   └── routes.py                 # Главная, о проекте
│   │
│   ├── static/                       # Статические файлы
│   │   ├── css/
│   │   │   ├── style.css             # Дополнительные стили
│   │   │   └── .gitkeep
│   │   ├── js/
│   │   │   ├── main.js               # Основной JavaScript
│   │   │   └── .gitkeep
│   │   └── uploads/
│   │       └── avatars/
│   │           ├── default-avatar.png # Дефолтный аватар
│   │           └── .gitkeep
│   │
│   └── templates/                    # Jinja2 шаблоны
│       ├── base.html                 # Базовый шаблон
│       ├── index.html                # Главная страница
│       ├── about.html                # О проекте
│       │
│       ├── auth/                     # Шаблоны авторизации
│       │   ├── login.html
│       │   └── register.html
│       │
│       ├── forum/                    # Шаблоны форума
│       │   ├── index.html            # Список топиков
│       │   ├── topic.html            # Просмотр топика
│       │   └── topic_create.html     # Создание топика
│       │
│       ├── chat/                     # Шаблоны чата
│       │   ├── index.html            # Список чатов
│       │   └── conversation.html     # Чат с пользователем
│       │
│       └── profile/                  # Шаблоны профиля
│           ├── view.html             # Просмотр профиля
│           ├── edit.html             # Редактирование
│           └── change_password.html  # Смена пароля
│
├── migrations/                       # Alembic миграции
│   ├── .gitkeep
│   ├── env.py                        # Конфигурация Alembic
│   ├── script.py.mako                # Шаблон миграции
│   └── versions/
│       └── 001_initial_migration.py  # Начальная миграция
│
├── nginx/                            # Конфигурация Nginx
│   ├── nginx.conf                    # Основной конфиг
│   └── conf.d/
│       ├── forum.conf                # Конфигурация для форума (HTTP/HTTPS)
│       └── .gitkeep
│
├── scripts/                          # Скрипты
│   ├── __init__.py
│   └── init_db.py                    # Инициализация БД с тестовыми данными
│
├── uploads/                          # Загруженные файлы (создается Docker)
│   ├── .gitkeep
│   ├── avatars/                      # Аватары пользователей
│   ├── posts/                        # Изображения в постах
│   └── chat/                         # Изображения в чате
│
├── certbot/                          # Данные Let's Encrypt (создается Docker)
│   ├── .gitkeep
│   ├── conf/                         # Сертификаты
│   └── www/                          # ACME challenge
│
├── config.py                         # Конфигурация приложения
├── run.py                            # Точка входа приложения
├── requirements.txt                  # Python зависимости
├── alembic.ini                       # Конфигурация Alembic
│
├── Dockerfile                        # Dockerfile для Flask приложения
├── docker-compose.yml                # Docker Compose конфигурация
├── .dockerignore                     # Исключения для Docker
├── .gitignore                        # Исключения для Git
│
├── entrypoint.sh                     # Entrypoint скрипт для Docker
├── init-letsencrypt.sh              # Скрипт получения SSL сертификата
├── create_default_avatar.py          # Создание дефолтного аватара
│
├── Makefile                          # Команды для управления проектом
│
├── README.md                         # Основная документация
├── QUICKSTART.md                     # Быстрый старт
├── DEPLOYMENT.md                     # Руководство по развертыванию
├── CONTRIBUTING.md                   # Руководство по участию
├── CHANGELOG.md                      # История изменений
├── PROJECT_STRUCTURE.md              # Этот файл
├── LICENSE                           # Лицензия MIT
│
└── .env.example                      # Пример файла окружения
```

## Основные компоненты

### Backend (Flask)

**config.py**
- Конфигурация для development/production
- Настройки БД, загрузок, безопасности

**app/__init__.py**
- Фабрика приложения
- Инициализация расширений (SQLAlchemy, Flask-Login, SocketIO)
- Регистрация blueprints

**app/models.py**
- `User` - пользователи
- `Topic` - топики форума
- `Post` - посты в топиках
- `ChatMessage` - сообщения в чате

### Blueprints

**auth** - Аутентификация
- Регистрация с валидацией
- Вход с запоминанием
- Выход
- Проверка уникальности email/username

**forum** - Форум
- Список топиков с пагинацией
- Просмотр топика с постами
- Создание топиков
- Добавление постов
- Загрузка изображений
- Удаление собственных постов

**chat** - Чат
- Список чатов
- Чат с пользователем (WebSocket)
- Отправка текста и изображений
- Индикатор "печатает..."
- Непрочитанные сообщения

**profile** - Профили
- Просмотр профиля
- Редактирование (имя, аватар)
- Смена пароля
- Статистика пользователя

**main** - Главные страницы
- Главная страница
- О проекте

### Frontend (Jinja2 + Bootstrap)

**base.html**
- Навигация
- Flash сообщения
- Footer
- Подключение Bootstrap, Socket.IO
- WebSocket для уведомлений

**Остальные шаблоны**
- Наследуются от base.html
- Используют Bootstrap 5 компоненты
- Адаптивные

### WebSocket (Flask-SocketIO)

**app/chat/events.py**
- `connect` - подключение
- `disconnect` - отключение
- `join_chat` - присоединение к чату
- `leave_chat` - выход из чата
- `send_message` - отправка сообщения
- `typing` - индикатор печати
- `mark_read` - отметка как прочитанное

События рассылаются в комнаты (rooms):
- `user_{id}` - персональная комната пользователя
- `chat_{id1}_{id2}` - комната для двух пользователей

### База данных (PostgreSQL)

**Таблицы:**
- `users` - пользователи
- `topics` - топики
- `posts` - посты
- `chat_messages` - сообщения чата

**Связи:**
- User ↔ Topics (1:N)
- User ↔ Posts (1:N)
- User ↔ ChatMessages (1:N, как sender и recipient)
- Topic ↔ Posts (1:N)

**Индексы:**
- email, username (уникальные)
- created_at (для сортировки)

### Docker

**Сервисы:**
- `web` - Flask приложение (Gunicorn + eventlet)
- `db` - PostgreSQL 15
- `nginx` - Reverse proxy
- `certbot` - SSL сертификаты

**Volumes:**
- `postgres_data` - данные БД
- `./uploads` - загруженные файлы
- `./certbot` - SSL сертификаты

**Network:**
- `forum_network` - bridge сеть

### Миграции (Alembic)

**migrations/env.py**
- Конфигурация Alembic
- Подключение к БД
- Загрузка моделей

**migrations/versions/**
- 001_initial_migration.py - создание всех таблиц

**Команды:**
```bash
flask db migrate -m "description"  # Создать миграцию
flask db upgrade                    # Применить миграцию
flask db downgrade                  # Откатить миграцию
```

### Nginx

**Функции:**
- Reverse proxy для Flask
- WebSocket proxy (Upgrade header)
- Статические файлы (uploads)
- SSL/TLS termination
- Gzip сжатие
- Security headers
- Rate limiting

### SSL/TLS (Let's Encrypt)

**init-letsencrypt.sh**
- Автоматическое получение сертификата
- Проверка домена через webroot
- Staging режим для тестирования

**certbot container**
- Автообновление каждые 12 часов
- Хранение сертификатов в volume

## Потоки данных

### Регистрация пользователя
1. Пользователь → auth/register.html (форма)
2. POST → auth/routes.py (валидация)
3. User.set_password() (хеширование)
4. SQLAlchemy → PostgreSQL (сохранение)
5. Redirect → auth/login.html

### Создание топика
1. Пользователь → forum/topic_create.html
2. POST → forum/routes.py
3. Topic() + db.session.add()
4. PostgreSQL (сохранение)
5. Redirect → forum/topic.html

### Отправка сообщения в чате
1. Пользователь → chat/conversation.html (WebSocket)
2. socket.emit('send_message') → JavaScript
3. SocketIO → app/chat/events.py
4. ChatMessage() + db.session.add()
5. emit('new_message') → комната чата
6. JavaScript → обновление UI

### Загрузка изображения
1. Пользователь → форма с enctype="multipart/form-data"
2. POST → route с request.files
3. utils.allowed_file() (проверка расширения)
4. utils.save_picture() (сохранение, опционально resize)
5. Filename → модель (User.avatar, Post.image, etc.)
6. File → uploads/{folder}/

## Безопасность

**Реализовано:**
- Хеширование паролей (Werkzeug)
- CSRF защита (Flask-WTF)
- SQL Injection защита (SQLAlchemy ORM)
- XSS защита (Jinja2 auto-escaping)
- Валидация файлов (расширения, размер)
- Security headers (Nginx)
- HTTPS/TLS
- Rate limiting (Nginx)

**Middleware:**
- @login_required - защита маршрутов
- Flask-Login - управление сессиями

## Производительность

**Оптимизации:**
- Gzip сжатие (Nginx)
- Кеширование статики (Nginx)
- Индексы БД
- Пагинация (SQLAlchemy)
- CDN ready (статические файлы через Nginx)
- Connection pooling (SQLAlchemy)
- eventlet workers (асинхронный I/O)

## Масштабируемость

**Можно добавить:**
- Redis для SocketIO message queue
- Celery для фоновых задач
- Multiple web workers
- Load balancer
- Отдельный сервер для PostgreSQL
- CDN для статики
- Memcached/Redis для кеширования

## Мониторинг

**Логи:**
- Flask app: docker logs forum_web
- PostgreSQL: docker logs forum_db
- Nginx: docker logs forum_nginx
- System: journalctl -xe

**Метрики:**
- docker stats (CPU, RAM, Network)
- PostgreSQL: pg_stat_*
- Можно добавить: Prometheus + Grafana

## Разработка

**Локальный запуск:**
1. Создать venv
2. pip install -r requirements.txt
3. Настроить .env (локальная БД)
4. flask db upgrade
5. python run.py

**Docker разработка:**
1. docker-compose up
2. Код монтируется через volume
3. Auto-reload включен (FLASK_ENV=development)

**Создание миграций:**
1. Изменить models.py
2. flask db migrate -m "description"
3. Проверить migrations/versions/
4. flask db upgrade

