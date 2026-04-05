FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

ARG APP_UID=999
ARG APP_GID=999

RUN groupadd --system --gid ${APP_GID} appgroup \
    && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home appuser

# Install dependencies
RUN pip install --no-cache-dir \
    mcp \
    httpx \
    "nanobot @ https://github.com/HKUDS/nanobot/archive/e7d371ec1e6531b28898ec2c869ef338e8dd46ec.zip"

COPY mcp/mcp-movies /app/mcp/mcp-movies
RUN pip install --no-cache-dir /app/mcp/mcp-movies

COPY nanobot /app/nanobot

RUN mkdir -p /app/nanobot/workspace/cron /app/nanobot/workspace/memory \
    && chown -R appuser:appgroup /app/nanobot/workspace \
    && chmod -R 755 /app/nanobot/workspace

USER appuser

WORKDIR /app

CMD ["python", "/app/nanobot/entrypoint.py"]
