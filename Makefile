# --- Default Values ---
CHECK_DIRS := .

# --- Run ---
help: # Отображение сообщения с доступными командами
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | while read -r l; do printf "\033[1;33m› $$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

init-migrations: # Инициализация среды миграций
	@uv run alembic init src/migrations

create-tables: # Создание таблиц базы данных
	@uv run alembic revision --autogenerate -m 'create db tables'

apply-migrations: # Применение миграции
	@uv run alembic upgrade head

run-app: # Запуск приложения
	@uv run uvicorn src.main:app --port 8000

run-app-dev: # Запуск приложения
	@uv run uvicorn src.main:app --port 8000 --reload

lint-check: # Check code for linting issues without making changes
	@uv run poe isort
	@uv run ruff check $(CHECK_DIRS)

lint-fix: # Fix linting issues using ruff
	@uv run ruff check --fix $(CHECK_DIRS)