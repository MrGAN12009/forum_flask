# Веб-форум на Flask

Полноценный веб-форум с поддержкой Docker, PostgreSQL, WebSocket чата и HTTPS.

## Возможности

- ✅ **Регистрация и авторизация** - безопасная система аутентификации с хешированием паролей
- ✅ **Форум** - создание топиков, обсуждения, загрузка изображений
- ✅ **Личные сообщения** - WebSocket чат в реальном времени
- ✅ **Профили пользователей** - аватары, статистика, настройки
- ✅ **Docker** - простое развертывание через docker-compose
- ✅ **HTTPS** - готовая конфигурация с Let's Encrypt
- ✅ **PostgreSQL** - надежная база данных
- ✅ **Миграции** - Alembic для управления схемой БД

## Технологии

### Backend
- **Flask** - веб-фреймворк
- **SQLAlchemy** - ORM
- **Flask-Login** - управление сессиями
- **Flask-SocketIO** - WebSocket для чата
- **Alembic** - миграции базы данных
- **PostgreSQL** - реляционная БД

### Frontend
- **Jinja2** - шаблонизация
- **Bootstrap 5** - UI фреймворк
- **Socket.IO** - WebSocket клиент

### Инфраструктура
- **Docker** - контейнеризация
- **Nginx** - reverse proxy
- **Let's Encrypt** - SSL сертификаты
- **Gunicorn** - WSGI сервер

## Структура проекта

```
forum/
├── app/                        # Главное приложение
│   ├── auth/                   # Авторизация и регистрация
│   ├── forum/                  # Форум (топики, посты)
│   ├── chat/                   # WebSocket чат
│   ├── profile/                # Профили пользователей
│   ├── main/                   # Главные страницы
│   ├── models.py               # Модели базы данных
│   ├── utils.py                # Вспомогательные функции
│   ├── templates/              # Jinja2 шаблоны
│   └── static/                 # Статические файлы
├── migrations/                 # Alembic миграции
├── nginx/                      # Конфигурация Nginx
│   ├── nginx.conf
│   └── conf.d/forum.conf
├── uploads/                    # Загруженные файлы
│   ├── avatars/
│   ├── posts/
│   └── chat/
├── docker-compose.yml          # Docker Compose конфигурация
├── Dockerfile                  # Dockerfile для Flask
├── requirements.txt            # Python зависимости
├── config.py                   # Конфигурация приложения
├── run.py                      # Точка входа
├── entrypoint.sh              # Entrypoint скрипт
└── init-letsencrypt.sh        # Скрипт для получения SSL
```

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Домен с DNS записями (для HTTPS)

### 1. Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone <your-repo>
cd forum

# Создайте .env файл
cp .env.example .env

# Отредактируйте .env и установите:
# - SECRET_KEY (используйте: python -c "import secrets; print(secrets.token_hex(32))")
# - DATABASE_URL (можно оставить как есть для Docker)
```

### 2. Запуск без HTTPS (для разработки)

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка логов
docker-compose logs -f web

# Приложение будет доступно на http://localhost
```

### 3. Инициализация базы данных

База данных автоматически инициализируется при первом запуске через миграции Alembic.

Для создания новых миграций:

```bash
# Войти в контейнер
docker-compose exec web bash

# Создать миграцию
flask db migrate -m "description"

# Применить миграцию
flask db upgrade
```

### 4. Настройка HTTPS (для продакшена)

#### Шаг 1: Настройка DNS
Убедитесь, что ваш домен указывает на сервер:
```
A запись: your-domain.com → IP сервера
A запись: www.your-domain.com → IP сервера
```

#### Шаг 2: Редактирование конфигурации

Отредактируйте `init-letsencrypt.sh`:
```bash
DOMAIN="your-domain.com"  # Ваш домен
EMAIL="your-email@example.com"  # Ваш email
```

#### Шаг 3: Получение сертификата

```bash
# Сделайте скрипт исполняемым
chmod +x init-letsencrypt.sh

# Запустите скрипт
./init-letsencrypt.sh
```

#### Шаг 4: Активация HTTPS в Nginx

Отредактируйте `nginx/conf.d/forum.conf`:
1. Замените `your-domain.com` на ваш домен
2. Раскомментируйте HTTPS server блок (строки с `# server {`)
3. Раскомментируйте редирект HTTP → HTTPS

```bash
# Перезапустите nginx
docker-compose restart nginx
```

#### Шаг 5: Автообновление сертификатов

Certbot автоматически обновляет сертификаты каждые 12 часов (настроено в docker-compose.yml).

Для ручного обновления:
```bash
docker-compose run --rm certbot renew
docker-compose restart nginx
```

## Управление

### Остановка сервисов

```bash
docker-compose down
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

### Резервное копирование базы данных

```bash
# Создание дампа
docker-compose exec db pg_dump -U postgres forum_db > backup.sql

# Восстановление из дампа
docker-compose exec -T db psql -U postgres forum_db < backup.sql
```

### Очистка и пересборка

```bash
# Остановить и удалить контейнеры
docker-compose down

# Удалить volumes (ВНИМАНИЕ: удалит базу данных!)
docker-compose down -v

# Пересобрать образы
docker-compose build --no-cache

# Запустить заново
docker-compose up -d
```

## Разработка

### Локальная разработка без Docker

```bash
# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте .env для локальной БД
DATABASE_URL=postgresql://user:password@localhost:5432/forum_db

# Запустите PostgreSQL локально
# Инициализируйте миграции
flask db upgrade

# Запустите приложение
python run.py
```

### Создание новых миграций

```bash
# Внесите изменения в модели (app/models.py)

# Создайте миграцию
docker-compose exec web flask db migrate -m "Description of changes"

# Проверьте созданную миграцию в migrations/versions/

# Применить миграцию
docker-compose exec web flask db upgrade
```

### Тестирование WebSocket

WebSocket чат работает на том же порту, что и основное приложение. Socket.IO автоматически подключается к серверу.

## Производительность

### Рекомендуемые настройки

Для продакшена рекомендуется:

1. **Gunicorn workers**: По умолчанию 1 eventlet worker. Для большей нагрузки можно увеличить в `entrypoint.sh`.

2. **PostgreSQL**: Настройте `postgresql.conf` для вашего оборудования.

3. **Nginx**: Включен gzip и настроены заголовки кеширования.

4. **Redis** (опционально): Для масштабирования WebSocket можно добавить Redis как message queue.

## Безопасность

### Реализовано

- ✅ Хеширование паролей (Werkzeug)
- ✅ CSRF защита (Flask-WTF)
- ✅ Валидация входных данных
- ✅ Проверка расширений файлов
- ✅ Ограничение размера загружаемых файлов (16MB)
- ✅ Security headers в Nginx
- ✅ HTTPS/TLS
- ✅ SQL injection защита (SQLAlchemy ORM)

### Рекомендации

- Используйте сильный `SECRET_KEY`
- Регулярно обновляйте зависимости
- Настройте firewall (только 80, 443, SSH)
- Используйте fail2ban для защиты от брутфорса
- Регулярно делайте резервные копии

## Решение проблем

### Приложение не запускается

```bash
# Проверьте логи
docker-compose logs web

# Проверьте, что БД запустилась
docker-compose logs db

# Пересоздайте контейнеры
docker-compose down
docker-compose up -d
```

### Ошибка подключения к БД

```bash
# Проверьте статус БД
docker-compose ps

# Проверьте переменные окружения
docker-compose exec web env | grep DATABASE

# Перезапустите сервисы
docker-compose restart
```

### WebSocket не работает

- Проверьте, что Nginx правильно проксирует WebSocket (proxy_set_header Upgrade)
- Проверьте логи браузера в DevTools
- Убедитесь, что используется eventlet worker в Gunicorn

### Проблемы с SSL сертификатом

```bash
# Проверьте логи certbot
docker-compose logs certbot

# Убедитесь что порт 80 доступен
curl -I http://your-domain.com/.well-known/acme-challenge/test

# Попробуйте staging режим
# В init-letsencrypt.sh установите STAGING=1
```

## Лицензия

MIT License

## Поддержка

Для вопросов и проблем создавайте Issues в репозитории.

---

**Создано с ❤️ используя Flask, PostgreSQL, Docker и современные веб-технологии**

