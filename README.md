# Movie Watchlist + Nanobot Assistant

A movie watchlist with a chat-style AI assistant that helps you pick what to watch.

## Product

**Problem:** People save movie names in notes apps, messages, or memory — all scattered. This stores them in one place and helps pick what to watch based on genre or mood.

**Version 1:** Simple list — add, view, remove, mark as watched.

**Version 2:** Nanobot assistant — talk to it in natural language, it searches your list and suggests what to watch.

## Architecture

```
[Browser — nanobot web UI at :8765]
           |
    [Nanobot Agent] ←→ [LLM via API]
           |
   [MCP: movie tools]
           |
    [FastAPI Backend] ←→ [SQLite]
```

## Quick Start

### 1. Configure environment

```sh
cp .env.docker.example .env.docker.secret
```

Edit `.env.docker.secret` and fill in:
- **`LLM_API_KEY`** — your Qwen/DashScope API key
- **`LLM_API_MODEL`** — e.g. `qwen-plus`

### 2. Start the stack

```sh
docker compose --env-file .env.docker.secret up --build -d
```

### 3. Use the app

- **Nanobot Chat UI:** http://localhost:8765 — talk to the movie assistant
- **Swagger API:** http://localhost:42002/docs — add movies directly via REST API

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/movies/` | List all movies |
| GET | `/movies/search?q=...` | Search by title/genre/notes |
| GET | `/movies/genre/{genre}` | Filter by genre |
| GET | `/movies/unwatched` | Only unwatched movies |
| POST | `/movies/` | Add a movie |
| PUT | `/movies/{id}` | Update a movie |
| DELETE | `/movies/{id}` | Remove a movie |

## Project Structure

```
├── backend/src/movie_backend/   # FastAPI + SQLite CRUD
├── mcp/mcp-movies/              # MCP server — 8 movie tools
├── nanobot/                     # AI agent
│   ├── workspace/               # SOUL.md, skills, memory
│   ├── entrypoint.py
│   ├── config.json
│   └── Dockerfile
├── docker-compose.yml
└── .env.docker.example
```
