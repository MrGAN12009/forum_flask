# Шпаргалка команд

Быстрый справочник полезных команд для работы с проектом.

## Docker

### Основные команды

```bash
# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Перезапуск сервисов
docker-compose restart

# Пересборка образов
docker-compose build

# Полная пересборка без кеша
docker-compose build --no-cache

# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx

# Статус контейнеров
docker-compose ps

# Остановка с удалением volumes (ОСТОРОЖНО: удалит БД!)
docker-compose down -v
```

### Работа с контейнерами

```bash
# Войти в контейнер web
docker-compose exec web bash

# Войти в контейнер БД
docker-compose exec db bash

# Выполнить команду в контейнере
docker-compose exec web python script.py

# PostgreSQL shell
docker-compose exec db psql -U postgres forum_db
```

## База данных

### Миграции

```bash
# Применить миграции
docker-compose exec web flask db upgrade

# Создать новую миграцию
docker-compose exec web flask db migrate -m "description"

# Откатить последнюю миграцию
docker-compose exec web flask db downgrade

# История миграций
docker-compose exec web flask db history

# Текущая версия
docker-compose exec web flask db current
```

### Backup и восстановление

```bash
# Создать backup
docker-compose exec db pg_dump -U postgres forum_db > backup.sql

# Создать сжатый backup
docker-compose exec db pg_dump -U postgres forum_db | gzip > backup.sql.gz

# Восстановить из backup
docker-compose exec -T db psql -U postgres forum_db < backup.sql

# Восстановить из сжатого backup
gunzip < backup.sql.gz | docker-compose exec -T db psql -U postgres forum_db

# Backup с датой
docker-compose exec db pg_dump -U postgres forum_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### SQL запросы

```bash
# Подключиться к БД
docker-compose exec db psql -U postgres forum_db

# Внутри psql:
\dt                  # Список таблиц
\d users             # Описание таблицы users
\q                   # Выход

# Прямой SQL запрос
docker-compose exec db psql -U postgres forum_db -c "SELECT * FROM users;"

# Подсчет пользователей
docker-compose exec db psql -U postgres forum_db -c "SELECT COUNT(*) FROM users;"

# Последние топики
docker-compose exec db psql -U postgres forum_db -c "SELECT title, created_at FROM topics ORDER BY created_at DESC LIMIT 5;"
```

## Flask

### Запуск и управление

```bash
# Запуск в режиме разработки (локально)
python run.py

# Запуск с Flask CLI
flask run

# Запуск на определенном порту
flask run --port 8000

# Запуск с внешним доступом
flask run --host 0.0.0.0

# Flask shell (интерактивная консоль)
docker-compose exec web flask shell

# В Flask shell:
>>> from app.models import User
>>> User.query.all()
>>> exit()
```

### Работа с приложением

```bash
# Инициализация БД с тестовыми данными
docker-compose exec web python scripts/init_db.py

# Создание дефолтного аватара
python create_default_avatar.py

# Проверка конфигурации
docker-compose exec web python -c "from config import config; print(config['production'].__dict__)"
```

## Python

### Управление зависимостями

```bash
# Установка зависимостей
pip install -r requirements.txt

# Обновление зависимостей
pip install --upgrade -r requirements.txt

# Создание requirements из текущего окружения
pip freeze > requirements.txt

# Установка конкретного пакета
pip install package-name

# Обновление конкретного пакета
pip install --upgrade package-name
```

### Виртуальное окружение

```bash
# Создание venv
python -m venv venv

# Активация (Linux/Mac)
source venv/bin/activate

# Активация (Windows)
venv\Scripts\activate

# Деактивация
deactivate
```

## Git

### Основные команды

```bash
# Клонирование репозитория
git clone https://github.com/username/forum.git

# Статус
git status

# Добавить все изменения
git add .

# Коммит
git commit -m "Description"

# Пуш
git push origin main

# Пулл
git pull origin main

# Просмотр истории
git log --oneline

# Создание ветки
git checkout -b feature-name

# Переключение ветки
git checkout main

# Слияние ветки
git merge feature-name
```

## Nginx

### Управление

```bash
# Перезагрузка конфигурации
docker-compose exec nginx nginx -s reload

# Проверка конфигурации
docker-compose exec nginx nginx -t

# Логи доступа
docker-compose exec nginx cat /var/log/nginx/access.log

# Логи ошибок
docker-compose exec nginx cat /var/log/nginx/error.log

# Следить за логами
docker-compose exec nginx tail -f /var/log/nginx/access.log
```

## SSL/TLS (Let's Encrypt)

### Получение сертификата

```bash
# Первоначальное получение
./init-letsencrypt.sh

# Ручное обновление
docker-compose run --rm certbot renew

# Тестовое обновление (dry-run)
docker-compose run --rm certbot renew --dry-run

# Получение нового сертификата для другого домена
docker-compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    --email your@email.com \
    --agree-tos \
    -d newdomain.com
```

### Проверка сертификата

```bash
# Информация о сертификате
docker-compose exec nginx openssl s_client -connect localhost:443 -servername your-domain.com

# Дата истечения
docker-compose run --rm certbot certificates

# Онлайн проверка
# https://www.ssllabs.com/ssltest/
```

## Мониторинг

### Производительность

```bash
# Статистика Docker контейнеров
docker stats

# Использование диска
df -h
du -sh /var/lib/docker

# Использование памяти
free -h

# Топ процессов
top
htop  # если установлен

# Сетевые подключения
netstat -tulpn
ss -tulpn
```

### Логи системы

```bash
# Системные логи
journalctl -xe

# Логи Docker daemon
journalctl -u docker

# Последние 100 строк системного лога
journalctl -n 100

# Следить за системным логом
journalctl -f
```

## Очистка

### Docker

```bash
# Удаление неиспользуемых образов
docker image prune

# Удаление неиспользуемых контейнеров
docker container prune

# Удаление неиспользуемых volumes
docker volume prune

# Полная очистка
docker system prune -a

# Очистка с volumes
docker system prune -a --volumes
```

### Логи

```bash
# Очистка логов Docker контейнеров
sudo sh -c "truncate -s 0 /var/lib/docker/containers/*/*-json.log"

# Очистка журнала systemd
sudo journalctl --vacuum-time=7d
sudo journalctl --vacuum-size=100M
```

### База данных

```bash
# VACUUM (очистка и оптимизация)
docker-compose exec db psql -U postgres forum_db -c "VACUUM ANALYZE;"

# Переиндексация
docker-compose exec db psql -U postgres forum_db -c "REINDEX DATABASE forum_db;"
```

## Отладка

### Проверка подключений

```bash
# Проверка портов
netstat -tulpn | grep LISTEN
ss -tulpn | grep LISTEN

# Проверка конкретного порта
nc -zv localhost 5000
nc -zv localhost 5432
nc -zv localhost 80

# Проверка доступности сайта
curl -I http://localhost
curl -I https://your-domain.com

# Проверка WebSocket
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Host: localhost" \
     http://localhost/socket.io/
```

### Проверка DNS

```bash
# Резолв домена
nslookup your-domain.com
dig your-domain.com
host your-domain.com

# Проверка всех записей
dig your-domain.com ANY
```

### Проверка SSL

```bash
# Проверка сертификата
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Дата истечения
echo | openssl s_client -connect your-domain.com:443 -servername your-domain.com 2>/dev/null | openssl x509 -noout -dates
```

## Полезные алиасы

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
# Docker Compose shortcuts
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcr='docker-compose restart'

# Forum specific
alias forum-logs='docker-compose logs -f web'
alias forum-shell='docker-compose exec web bash'
alias forum-db='docker-compose exec db psql -U postgres forum_db'
alias forum-backup='docker-compose exec db pg_dump -U postgres forum_db > backup_$(date +%Y%m%d_%H%M%S).sql'

# Git shortcuts
alias gs='git status'
alias ga='git add'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline'
```

## Makefile команды

Если используете Makefile:

```bash
# Помощь
make help

# Сборка
make build

# Запуск
make up

# Остановка
make down

# Перезапуск
make restart

# Логи
make logs
make logs-web
make logs-db

# Миграции
make migrate
make migrate-create MSG="description"

# База данных
make init-db
make db-shell
make backup
make restore

# SSL
make ssl

# Создание аватара
make avatar

# Полная настройка
make setup

# Разработка
make dev

# Статистика
make ps
make stats
```

## Переменные окружения

### Просмотр

```bash
# Все переменные в контейнере
docker-compose exec web env

# Конкретная переменная
docker-compose exec web printenv DATABASE_URL

# Из .env файла
cat .env
```

### Установка

```bash
# Временная установка
export FLASK_ENV=development

# В .env файле
echo "FLASK_ENV=development" >> .env

# В docker-compose.yml
environment:
  FLASK_ENV: development
```

## Генерация секретов

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
openssl rand -base64 32

# /dev/urandom
cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1
```

## Тестирование

```bash
# Запуск pytest (если настроен)
pytest
pytest -v
pytest --cov=app

# Конкретный файл
pytest tests/test_auth.py

# Конкретный тест
pytest tests/test_auth.py::test_login

# С выводом print
pytest -s
```

## Безопасность

```bash
# Проверка открытых портов
nmap localhost

# Статус firewall
sudo ufw status

# Проверка обновлений безопасности
sudo apt update
sudo apt list --upgradable

# Аудит зависимостей Python
pip install safety
safety check

# Сканирование на уязвимости (requires npm)
npm install -g snyk
snyk test
```

## Быстрые проверки

```bash
# Все ли контейнеры запущены?
docker-compose ps

# Работает ли веб-сервер?
curl -I http://localhost

# Подключается ли к БД?
docker-compose exec web python -c "from app import db; print('OK')"

# Работает ли WebSocket?
curl http://localhost/socket.io/

# Есть ли пользователи?
docker-compose exec db psql -U postgres forum_db -c "SELECT COUNT(*) FROM users;"

# Размер БД
docker-compose exec db psql -U postgres forum_db -c "SELECT pg_size_pretty(pg_database_size('forum_db'));"
```

---

**Совет**: Добавьте эту страницу в закладки для быстрого доступа к командам!

