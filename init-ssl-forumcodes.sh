#!/bin/bash

# Скрипт для получения SSL сертификата для forumcodes.online

DOMAIN="forumcodes.online"
EMAIL="admin@forumcodes.online"  # Измените на ваш реальный email
STAGING=0  # 0 = production, 1 = testing

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Получение SSL сертификата для $DOMAIN ===${NC}"

# Создание директорий
echo -e "${YELLOW}Создание директорий...${NC}"
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
echo -e "${YELLOW}Проверка статуса nginx...${NC}"
if ! docker-compose ps | grep -q forum_nginx.*Up; then
    echo -e "${YELLOW}Запуск docker-compose...${NC}"
    docker-compose up -d
    sleep 10
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
    echo -e "${YELLOW}Теперь обновите nginx/conf.d/forumcodes.conf:${NC}"
    echo -e "  1. Раскомментируйте HTTPS server блок (строки с #)"
    echo -e "  2. Раскомментируйте редирект в HTTP блоке (строка 17-19)"
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

