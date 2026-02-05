# ---------- Build Stage ----------
FROM ghcr.io/astral-sh/uv:python3.13-bookworm AS builder

WORKDIR /app

# Настройки UV
ARG TORCH_DEPENDENCY
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=never


# Сначала только зависимости (используем кеш слоев)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev;

# Копируем исходники и устанавливаем проект
COPY src/ ./src/
COPY pyproject.toml uv.lock README.md ./

# Устанавливаем зависимости в виртуальное окуружение
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev;


# ---------- Runtime Stage ----------
FROM python:3.13-slim-bookworm

# Создаем пользователя для безопасности
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1001 appuser

WORKDIR /app

# Копируем только то, что реально нужно
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src

# Настройки среды
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=${API_PORT}

USER appuser

# Открываем порт наружу
EXPOSE $PORT

# Используем shell для подстановки переменной, но exec для сохранения PID 1
CMD ["sh", "-c", "exec uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT} --workers 1 --loop uvloop --no-access-log"]
