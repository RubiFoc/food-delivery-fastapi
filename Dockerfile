# Базовый образ для сборки
FROM python:3.12-slim-bullseye as base

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем необходимые файлы для Poetry
COPY pyproject.toml poetry.lock /app/

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Копируем исходный код
COPY app /app/

# Переход к финальному слою для приложения FastAPI
FROM base as fastapi

# Открываем порт для приложения
EXPOSE 8000

# Команда для запуска FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
