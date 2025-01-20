FROM python:3.11-bookworm

ENV POETRY_VERSION=1.8.4

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY . .
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

ENTRYPOINT [ "poetry", "run", "python3", "-m", "pageindexer.main"]
