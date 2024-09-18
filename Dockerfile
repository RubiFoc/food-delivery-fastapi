FROM python:3.12-slim-bullseye as base

WORKDIR /app

COPY pyproject.toml poetry.lock .env /app/

RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

COPY app /app/

FROM base as fastapi
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
