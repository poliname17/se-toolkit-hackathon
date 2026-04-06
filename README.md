# Movie Watchlist + Nanobot Assistant

A movie watchlist with a chat-style AI assistant that helps you pick what to watch.

## Product

**Problem:** People save movie names in notes apps, messages, or memory — all scattered. This stores them in one place and helps pick what to watch based on genre or mood.

**Version 1:** Simple list — add, remove, mark as watched.

**Version 2:** Nanobot assistant suggests what to watch based on your question. It can recommend something new or suggest films from your watchlist.

### Use the web service with MovieBot

http://10.93.25.91:3000

### How it works

```
[Browser — Frontend UI at :3000]
     |
     | GET /api/movies/  →  Backend API
     | WebSocket /ws     →  MovieChat Agent
     |
[Backend API (FastAPI)] ←→ [SQLite — movies.db]
     |
[MovieChat Agent] ←→ [qwen-code-api proxy] ←→ [DashScope LLM]
     |
     └── 7 tools: list, add, update, delete, search, unwatched, recommend_external
```

When you type a message, the LLM decides which tool to call — search your watchlist, add a movie, or recommend something entirely new.

## Architecture

- **backend/** — FastAPI + SQLite CRUD for movies.
- **chat/** — Lightweight WebSocket agent with tool-calling (no nanobot framework needed).
- **qwen-code-api/** — LLM auth proxy (built from Lab 8 source).
- **frontend/** — Single-page app (HTML/CSS/JS) with chat + watchlist side by side, served by nginx.
- **movie-chat/** — The chat service source (Python, websockets, openai, httpx).

## Quick Start

1. Copy `.env.docker.secret` and fill in your LLM key.
2. `docker compose --env-file .env.docker.secret up --build -d --remove-orphans`
3. Open the web app (see URL above).

## Project Structure

```
├── backend/src/movie_backend/   # FastAPI + SQLite CRUD
├── chat/                        # WebSocket agent Dockerfile
├── frontend/                    # Single-page HTML app + nginx config
├── movie-chat/src/movie_chat/   # Agent code — tools, LLM calls, WebSocket handler
├── qwen-code-api/               # LLM auth proxy (copied from Lab 8)
├── docker-compose.yml
├── .env.docker.example
└── .env.docker.secret
```
