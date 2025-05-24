FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==1.8.3"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000"]