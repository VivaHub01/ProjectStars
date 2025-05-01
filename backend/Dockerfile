FROM python:3.12-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock alembic.ini ./

# Установка Python-зависимостей
RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root && \
    pip install asyncpg

# Копирование исходного кода
COPY ./src ./src

CMD ["sh", "-c", "python -c 'import time, os; time.sleep(5)' && \
     alembic upgrade head && \
     poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000"]