# Makefile для управления проектом форума

.PHONY: help build up down restart logs clean migrate init-db ssl

help: ## Показать эту справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Собрать Docker образы
	docker-compose build

up: ## Запустить все сервисы
	docker-compose up -d
	@echo "✓ Приложение запущено на http://localhost"

down: ## Остановить все сервисы
	docker-compose down

restart: ## Перезапустить все сервисы
	docker-compose restart

logs: ## Показать логи всех сервисов
	docker-compose logs -f

logs-web: ## Показать логи веб-приложения
	docker-compose logs -f web

logs-db: ## Показать логи базы данных
	docker-compose logs -f db

logs-nginx: ## Показать логи nginx
	docker-compose logs -f nginx

clean: ## Остановить и удалить все контейнеры и volumes (ВНИМАНИЕ: удалит БД!)
	docker-compose down -v
	rm -rf uploads/*
	mkdir -p uploads/avatars uploads/posts uploads/chat

rebuild: clean build up ## Полная пересборка проекта

migrate: ## Применить миграции базы данных
	docker-compose exec web flask db upgrade

migrate-create: ## Создать новую миграцию (использование: make migrate-create MSG="description")
	docker-compose exec web flask db migrate -m "$(MSG)"

init-db: ## Инициализировать БД с тестовыми данными
	docker-compose exec web python scripts/init_db.py

shell: ## Открыть shell в контейнере приложения
	docker-compose exec web bash

db-shell: ## Открыть PostgreSQL shell
	docker-compose exec db psql -U postgres forum_db

backup: ## Создать резервную копию базы данных
	docker-compose exec db pg_dump -U postgres forum_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✓ Резервная копия создана"

restore: ## Восстановить БД из backup.sql
	docker-compose exec -T db psql -U postgres forum_db < backup.sql
	@echo "✓ База данных восстановлена"

ssl: ## Получить SSL сертификат
	./init-letsencrypt.sh

avatar: ## Создать дефолтный аватар
	python create_default_avatar.py

setup: avatar build up migrate init-db ## Полная настройка проекта с нуля
	@echo "✓ Проект настроен и готов к использованию!"
	@echo "  Откройте http://localhost в браузере"
	@echo "  Тестовые пользователи: user1-3@example.com / password123"

dev: ## Запустить в режиме разработки
	@echo "Запуск в режиме разработки..."
	python run.py

install: ## Установить Python зависимости локально
	pip install -r requirements.txt

test: ## Запустить тесты (заглушка)
	@echo "Тесты пока не реализованы"

format: ## Форматировать код (заглушка)
	@echo "Форматирование не настроено"

ps: ## Показать статус контейнеров
	docker-compose ps

stats: ## Показать статистику использования ресурсов
	docker stats forum_web forum_db forum_nginx --no-stream

