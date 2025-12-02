# --- Default Values ---
CHECK_DIRS := .

# --- Run ---
help: # Отображение сообщения с доступными командами
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | while read -r l; do printf "\033[1;33m› $$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

init-migrations: # Инициализация среды миграций
	@uv run alembic init src/migrations

init-async-migrations: # Инициализация среды миграций для ассинхронного взаимодействия
	@uv run alembic init -t async src/migrations

database-up: # Инициализация среды миграций для ассинхронного взаимодействия
	@docker compose up -d

database-down: # Инициализация среды миграций для ассинхронного взаимодействия
	@docker compose down

create-tables-migration: # Создание таблиц базы данных
	@uv run alembic revision --autogenerate -m 'Initial migration for PostgreSQL'

apply-migrations: # Применение миграции
	@uv run alembic upgrade head

run-app: # Запуск приложения
	@nohup uv run uvicorn src.main:app --port 8000 &> backend_server.log

run-app-dev: # Запуск приложения
	@uv run uvicorn src.main:app --port 8000 --reload

lint-check: # Проверка кода на наличие ошибок без внесения изменений
	@uv run poe isort
	@uv run ruff check $(CHECK_DIRS)

lint-fix: # Исправление ошибок в коде с помощью ruff
	@uv run ruff check --fix $(CHECK_DIRS)