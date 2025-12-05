#!/bin/bash

# Скрипт для получения SSL сертификата через Let's Encrypt

# ВАЖНО: Перед запуском замените your-domain.com на ваш реальный домен
DOMAIN="your-domain.com"
EMAIL="your-email@example.com"  # Email для уведомлений от Let's Encrypt
STAGING=0  # Установите в 1 для тестового режима (staging)

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Инициализация Let's Encrypt для $DOMAIN ===${NC}"

# Проверка, что домен заменен
if [ "$DOMAIN" = "your-domain.com" ]; then
    echo -e "${RED}ОШИБКА: Пожалуйста, замените 'your-domain.com' на ваш реальный домен в скрипте!${NC}"
    exit 1
fi

# Проверка, что email заменен
if [ "$EMAIL" = "your-email@example.com" ]; then
    echo -e "${RED}ОШИБКА: Пожалуйста, замените 'your-email@example.com' на ваш реальный email в скрипте!${NC}"
    exit 1
fi

# Создание директорий
echo -e "${YELLOW}Создание необходимых директорий...${NC}"
mkdir -p certbot/conf
mkdir -p certbot/www

# Определение staging опции
if [ $STAGING != "0" ]; then
    STAGING_ARG="--staging"
    echo -e "${YELLOW}Используется STAGING режим (тестовые сертификаты)${NC}"
else
    STAGING_ARG=""
fi

# Проверка, что nginx запущен
echo -e "${YELLOW}Проверка состояния nginx...${NC}"
if ! docker-compose ps | grep -q forum_nginx.*Up; then
    echo -e "${YELLOW}Запуск docker-compose...${NC}"
    docker-compose up -d
    sleep 5
fi

# Получение сертификата
echo -e "${YELLOW}Запуск certbot для получения сертификата...${NC}"
docker-compose run --rm certbot certonly --webroot \
    --webroot-path=/var/www/certbot \
    $STAGING_ARG \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Сертификат успешно получен!${NC}"
    echo -e "${YELLOW}Теперь обновите nginx/conf.d/forum.conf:${NC}"
    echo -e "  1. Замените 'your-domain.com' на '$DOMAIN'"
    echo -e "  2. Раскомментируйте HTTPS server блок"
    echo -e "  3. Раскомментируйте редирект в HTTP блоке"
    echo -e "${YELLOW}После этого перезапустите nginx:${NC}"
    echo -e "  docker-compose restart nginx"
else
    echo -e "${RED}✗ Ошибка при получении сертификата!${NC}"
    echo -e "${YELLOW}Убедитесь что:${NC}"
    echo -e "  - Домен $DOMAIN указывает на этот сервер"
    echo -e "  - Порт 80 открыт и доступен из интернета"
    echo -e "  - nginx запущен и работает"
    exit 1
fi

