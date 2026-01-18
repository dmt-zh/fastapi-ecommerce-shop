# --- Default Values ---
CHECK_DIRS := .

# --- Run ---
help: # Отображение сообщения с доступными командами
	@grep -E '^[a-zA-Z0-9 -]+:.*#' Makefile | \
		awk -F'#' '{printf "› \033[1;33m%s\033[00m#%s\n", $$1, $$2}' | \
		column -t -s'#' | \
		sed 's/:  /: /g'

init-migrations: # Инициализация среды миграций
	@uv run alembic init -t async src/migrations

database-up: # Запуск базы данных PostgreSQL в контейнере
	@docker compose up -d

database-down: # Остановка базы данных PostgreSQL
	@docker compose down

create-tables-migration: # Создание таблиц базы данных
	@uv run alembic revision --autogenerate -m 'Initial migration for PostgreSQL'

apply-migrations: # Применение миграции
	@uv run alembic upgrade head

run-app: # Запуск приложения
	@nohup uv run uvicorn src.api.main:app --port 8000 &> backend_server.log

run-app-dev: # Запуск приложения во время разработки
	@uv run uvicorn src.api.main:app --port 8000 --reload

lint-check: # Проверка кода на наличие ошибок без внесения изменений
	@uv run poe isort
	@uv run ruff check $(CHECK_DIRS)

lint-fix: # Исправление ошибок в коде с помощью ruff
	@uv run ruff check --fix $(CHECK_DIRS)

type-check: # Cтатическая проверка типов в Python
	@uv run poe all