FROM python:3.12-slim-bookworm

ENV PYTHONPATH=/app

WORKDIR /app

COPY movie-chat/src/movie_chat /app/movie_chat

RUN pip install --no-cache-dir httpx websockets openai

CMD ["python", "-m", "movie_chat"]
