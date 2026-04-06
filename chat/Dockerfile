FROM python:3.12-slim-bookworm

WORKDIR /app

COPY movie-chat/pyproject.toml /app/movie-chat/pyproject.toml

RUN pip install --no-cache-dir httpx websockets openai

COPY movie-chat/src /app/movie-chat/src

CMD ["python", "-m", "movie_chat"]
