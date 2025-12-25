# Инструкция по обновлению проекта с Email Verification

## Что добавлено:
- ✅ Подтверждение email при регистрации
- ✅ Отправка 6-значного кода на почту
- ✅ Код действует 1 час
- ✅ Повторная отправка кода
- ✅ Проверка email перед входом

---

## Шаг 1: Настройка почты (Gmail пример)

### Вариант A: Gmail с App Password (рекомендуется)

1. Зайдите в https://myaccount.google.com/
2. Включите двухфакторную аутентификацию
3. Создайте App Password: https://myaccount.google.com/apppasswords
4. Используйте этот пароль в .env

### Вариант B: Другой SMTP сервер

Можете использовать любой SMTP сервер (SendGrid, Mailgun, etc.)

---

## Шаг 2: Обновление .env файла

Добавьте в ваш `.env` файл (на сервере):

```bash
# Email настройки
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_DEFAULT_SENDER=noreply@forumcodes.online
```

**Важно:** Замените `your-email@gmail.com` и `your-app-password-here` на ваши данные!

---

## Шаг 3: Перезагрузка проекта БЕЗ потери SSL

На сервере выполните:

```bash
cd ~/forum_flask

# 1. Остановка контейнеров (SSL НЕ удаляется!)
docker compose down

# 2. Получение обновлений
git pull

# 3. Пересборка образа (установка Flask-Mail)
docker compose build

# 4. Применение миграции БД
docker compose up -d db
sleep 5
docker compose exec web flask db upgrade

# 5. Запуск всех контейнеров
docker compose up -d

# 6. Проверка
docker compose ps
docker compose logs web --tail 50
```

---

## Шаг 4: Проверка работы

1. Откройте https://forumcodes.online/auth/register
2. Зарегистрируйтесь с РЕАЛЬНЫМ email
3. Проверьте почту - должно прийти письмо с кодом
4. Введите 6-значный код
5. Войдите в систему

---

## Резервное копирование перед обновлением

```bash
# Бэкап БД
docker compose exec db pg_dump -U postgres forum_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Бэкап загруженных файлов
tar -czf uploads_backup_$(date +%Y%m%d_%H%M%S).tar.gz uploads/

# Бэкап SSL сертификатов (на всякий случай)
tar -czf ssl_backup_$(date +%Y%m%d_%H%M%S).tar.gz certbot/conf/
```

---

## Откат изменений (если что-то пошло не так)

```bash
# Остановка
docker compose down

# Откат миграции
docker compose up -d db
docker compose exec web flask db downgrade

# Возврат к старой версии кода
git reset --hard HEAD~1

# Перезапуск
docker compose up -d --build
```

---

## Важные файлы:

- `app/models.py` - добавлены поля для email verification
- `app/auth/routes.py` - обновлены роуты регистрации/логина + новые роуты
- `app/utils.py` - функции отправки email
- `app/templates/auth/verify_email.html` - страница подтверждения
- `config.py` - настройки почты
- `requirements.txt` - добавлен Flask-Mail
- `migrations/versions/002_email_verification.py` - миграция БД

---

## Проверка SSL после обновления

```bash
# SSL сертификаты должны остаться на месте
ls -la certbot/conf/live/forumcodes.online/

# Проверка HTTPS
curl -I https://forumcodes.online
```

Сертификаты в `certbot/conf/` НЕ удаляются при `docker compose down`!

---

## Troubleshooting

### Email не отправляется?

```bash
# Проверьте логи
docker compose logs web | grep -i mail

# Проверьте настройки
docker compose exec web python3 -c "from flask import Flask; from app import create_app; app = create_app('production'); print(app.config['MAIL_USERNAME'])"
```

### Ошибка миграции?

```bash
# Посмотрите текущую версию БД
docker compose exec web flask db current

# История миграций
docker compose exec web flask db history
```

### HTTPS не работает?

```bash
# Проверьте nginx
docker compose logs nginx --tail 20

# Убедитесь, что сертификаты на месте
docker compose exec nginx ls -la /etc/letsencrypt/live/forumcodes.online/
```

---

## Тестирование в development

Для локального тестирования без реальной отправки email:

```bash
# В .env установите
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false

# Запустите fake SMTP сервер
python3 -m smtpd -n -c DebuggingServer localhost:1025
```

Все "отправленные" письма будут выводиться в консоль.

