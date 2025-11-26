### Инициализация и запуск проекта

Устанавливаем пакетный менеджер [uv](https://docs.astral.sh/uv/getting-started/installation/):
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Чтобы изменения внесённые в файл `bashrc` в текущем сеансе терминала вступили в силу, файл необходимо перезагрузить:
```sh
source ~/.bashrc
```

Копируем репозиторий:
```sh
git clone https://github.com/dmt-zh/fastapi-ecommerce-shop.git && cd fastapi-ecommerce-shop
```

Создаем виртуальное окружение и устанавливаем зависимости:
```sh
uv sync --locked
```

Для установки дополнительных зависимостей проверки кода (линтеров):
```sh
uv sync --group lint
```

<hr>


#### Запуск приложения
uv run uvicorn main:app --port 8000 --reload

--reload: Включает автоматическую перезагрузку при изменении кода (только для разработки)

#### Документация по API
http://127.0.0.1:8000/docs/

#### Запуск приложения
uv run uvicorn src.main:app --port 8000 --reload

#### Запуск отдельного скрипта
uv run -m src.models.categories

#### Инициализация среды миграций
uv run alembic init src/migrations

#### Создание таблиц базы данных
uv run alembic revision --autogenerate -m 'create db tables'

#### Применение миграции
uv run alembic upgrade head
