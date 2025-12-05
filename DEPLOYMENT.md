# Руководство по развертыванию

Подробная инструкция по развертыванию форума на продакшен сервере.

## Требования к серверу

### Минимальные требования
- **CPU**: 1 ядро
- **RAM**: 1 GB
- **Диск**: 10 GB SSD
- **ОС**: Ubuntu 20.04/22.04 LTS или Debian 11+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### Рекомендуемые требования
- **CPU**: 2+ ядра
- **RAM**: 2+ GB
- **Диск**: 20+ GB SSD
- **ОС**: Ubuntu 22.04 LTS

## Предварительная настройка сервера

### 1. Обновление системы

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Установка Docker

```bash
# Удаление старых версий
sudo apt remove docker docker-engine docker.io containerd runc

# Установка зависимостей
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Добавление Docker GPG ключа
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавление репозитория
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Проверка установки
sudo docker --version
sudo docker compose version
```

### 3. Настройка пользователя

```bash
# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Выйдите и войдите снова для применения изменений
exit
```

### 4. Настройка firewall

```bash
# Установка UFW
sudo apt install -y ufw

# Базовые правила
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Разрешение SSH
sudo ufw allow 22/tcp

# Разрешение HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Включение firewall
sudo ufw enable
sudo ufw status
```

## Развертывание приложения

### 1. Клонирование репозитория

```bash
# Перейдите в домашнюю директорию
cd ~

# Клонируйте репозиторий
git clone https://github.com/your-username/forum.git
cd forum
```

### 2. Настройка окружения

```bash
# Создайте .env файл
cat > .env << EOF
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=postgresql://postgres:$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)@db:5432/forum_db
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif
EOF

# Защитите файл
chmod 600 .env
```

### 3. Настройка PostgreSQL пароля

Отредактируйте `docker-compose.yml` и установите сильный пароль:

```yaml
db:
  environment:
    POSTGRES_PASSWORD: your-strong-password-here
```

Также обновите `DATABASE_URL` в `.env` с этим паролем.

### 4. Создание дефолтного аватара

```bash
# Установите Pillow если нужно
python3 -m pip install Pillow

# Создайте аватар
python3 create_default_avatar.py
```

### 5. Настройка DNS

Убедитесь, что ваш домен указывает на IP сервера:

```
A запись: your-domain.com → 123.456.789.0
A запись: www.your-domain.com → 123.456.789.0
```

Проверьте DNS:
```bash
dig your-domain.com +short
```

### 6. Запуск приложения

```bash
# Сборка и запуск
docker compose up -d

# Проверка логов
docker compose logs -f
```

### 7. Получение SSL сертификата

```bash
# Отредактируйте init-letsencrypt.sh
nano init-letsencrypt.sh
# Измените DOMAIN и EMAIL

# Сделайте скрипт исполняемым
chmod +x init-letsencrypt.sh

# Запустите
./init-letsencrypt.sh
```

### 8. Активация HTTPS

```bash
# Отредактируйте nginx конфигурацию
nano nginx/conf.d/forum.conf

# Замените your-domain.com на ваш домен
# Раскомментируйте HTTPS блок

# Перезапустите nginx
docker compose restart nginx
```

### 9. Инициализация данных (опционально)

```bash
# Создайте тестовых пользователей
docker compose exec web python scripts/init_db.py
```

## Мониторинг и обслуживание

### Просмотр логов

```bash
# Все логи
docker compose logs -f

# Конкретный сервис
docker compose logs -f web
docker compose logs -f db
docker compose logs -f nginx
```

### Резервное копирование

#### Автоматическое резервное копирование

Создайте cron задачу:

```bash
# Создайте скрипт
cat > ~/backup-forum.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups/forum"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup базы данных
cd ~/forum
docker compose exec -T db pg_dump -U postgres forum_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup файлов
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz uploads/

# Удаление старых бэкапов (старше 7 дней)
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

# Сделайте исполняемым
chmod +x ~/backup-forum.sh

# Добавьте в crontab (каждый день в 2:00)
crontab -e
# Добавьте строку:
0 2 * * * /root/backup-forum.sh >> /var/log/forum-backup.log 2>&1
```

#### Восстановление из backup

```bash
# Остановите приложение
cd ~/forum
docker compose down

# Восстановите БД
gunzip < /root/backups/forum/db_20240101_020000.sql.gz | docker compose exec -T db psql -U postgres forum_db

# Восстановите файлы
tar -xzf /root/backups/forum/uploads_20240101_020000.tar.gz

# Запустите приложение
docker compose up -d
```

### Обновление приложения

```bash
cd ~/forum

# Создайте backup
docker compose exec db pg_dump -U postgres forum_db > backup_before_update.sql

# Остановите приложение
docker compose down

# Обновите код
git pull

# Пересоберите образы
docker compose build

# Запустите
docker compose up -d

# Примените миграции
docker compose exec web flask db upgrade

# Проверьте логи
docker compose logs -f
```

### Мониторинг ресурсов

```bash
# Статистика контейнеров
docker stats

# Использование диска
df -h
du -sh ~/forum/*

# Логи системы
journalctl -xe

# Логи Docker
docker compose logs --tail=100
```

### Очистка старых данных

```bash
# Очистка неиспользуемых Docker образов
docker system prune -a

# Очистка старых логов
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

## Масштабирование

### Увеличение производительности

#### 1. Добавление Redis для WebSocket

Добавьте в `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  container_name: forum_redis
  restart: always
  networks:
    - forum_network
```

Обновите `config.py`:

```python
SOCKETIO_MESSAGE_QUEUE = 'redis://redis:6379'
```

#### 2. Увеличение workers

В `entrypoint.sh` измените:

```bash
exec gunicorn --worker-class eventlet -w 4 --bind 0.0.0.0:5000 "run:app"
```

#### 3. Настройка PostgreSQL

Создайте `postgresql.conf` и добавьте в volume.

### Load Balancing

Для высоких нагрузок рассмотрите:
- Несколько экземпляров web контейнера
- Внешний Load Balancer (HAProxy, AWS ELB)
- CDN для статических файлов
- Отдельный сервер для PostgreSQL

## Безопасность

### Регулярные обновления

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker compose pull
docker compose up -d
```

### Fail2ban

Защита от брутфорса:

```bash
# Установка
sudo apt install -y fail2ban

# Создайте jail для nginx
sudo cat > /etc/fail2ban/jail.d/nginx.conf << EOF
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
findtime = 600
bantime = 3600
EOF

# Перезапустите
sudo systemctl restart fail2ban
sudo fail2ban-client status
```

### SSL/TLS Hardening

Nginx конфигурация уже включает базовые настройки безопасности.

Дополнительно можно добавить:
- OCSP Stapling
- CAA DNS записи
- Более строгие cipher suites

## Мониторинг производительности

### Настройка Prometheus + Grafana (опционально)

```yaml
# Добавьте в docker-compose.yml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

## Решение проблем

### Проблемы с памятью

```bash
# Проверка использования
free -h
docker stats

# Увеличение swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Проблемы с диском

```bash
# Очистка логов Docker
sudo sh -c "truncate -s 0 /var/lib/docker/containers/*/*-json.log"

# Очистка неиспользуемых образов
docker system prune -a
```

### Проблемы с производительностью БД

```bash
# Переиндексация
docker compose exec db psql -U postgres forum_db -c "REINDEX DATABASE forum_db;"

# VACUUM
docker compose exec db psql -U postgres forum_db -c "VACUUM ANALYZE;"
```

## Checklist перед запуском

- [ ] Сервер обновлен
- [ ] Docker установлен
- [ ] Firewall настроен
- [ ] DNS настроен
- [ ] .env файл создан с сильным SECRET_KEY
- [ ] PostgreSQL пароль изменен
- [ ] Дефолтный аватар создан
- [ ] SSL сертификат получен
- [ ] HTTPS включен в nginx
- [ ] Backup настроен
- [ ] Мониторинг настроен

## Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

