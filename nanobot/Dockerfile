ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY --from=workspace pyproject.toml uv.lock /app/
COPY --from=workspace mcp/mcp-movies /app/mcp/mcp-movies
COPY --from=workspace nanobot/pyproject.toml /app/nanobot/pyproject.toml

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot

COPY --from=workspace nanobot/. /app/nanobot/

FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

ARG APP_UID=999
ARG APP_GID=999

RUN groupadd --system --gid ${APP_GID} appgroup \
    && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home appuser

COPY --from=builder --chown=appuser:appgroup /app /app

RUN mkdir -p /app/nanobot/workspace/cron /app/nanobot/workspace/memory \
    && chown -R appuser:appgroup /app/nanobot/workspace \
    && chmod -R 755 /app/nanobot/workspace

ENV PATH="/app/.venv/bin:$PATH"

USER appuser

WORKDIR /app

CMD ["python", "/app/nanobot/entrypoint.py"]
