#!/bin/sh
alembic revision --autogenerate -m "init"
alembic upgrade head
exec poetry run uvicorn src.main:app --host 0.0.0.0 --port ${APP_PORT:-8000}