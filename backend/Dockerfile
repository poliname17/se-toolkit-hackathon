FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    pydantic

COPY src/ ./src/

EXPOSE 8000

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "movie_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
