# Movie Watchlist + Nanobot Assistant

A web app to save movies you want to watch, plus a chat-style nanobot that recommends from your list by genre or mood.

## Product

**Problem:** People save movie names in notes apps, messages, or memory — all scattered. This product stores them in one place and later helps pick what to watch based on mood or genre.

**Version 1:** A simple list of movies to watch — add, view, remove, and mark as watched.

**Version 2:** A nanobot assistant that helps users navigate their watchlist and suggests options based on genre, mood, or what they're in the mood for.

## Architecture

```
[Browser - Flutter Web Client]
            |
            v
    [Nanobot Agent] ←→ [LLM via Qwen Code API]
            |
    [Movie MCP Tools]
            |
    [FastAPI Backend] ←→ [PostgreSQL]
```

### What's included

- **backend/** — FastAPI service with CRUD endpoints for the movie watchlist.
- **nanobot/** — Nanobot agent configured as a movie assistant.
- **mcp/mcp-movies/** — MCP server that gives the agent tools to query the watchlist.
- **nanobot-websocket-channel/** — WebSocket bridge + Flutter web chat client.
- **docker-compose.yml** — Runs everything together.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- A Qwen API key (or any OpenAI-compatible LLM endpoint)

### 1. Clone the repo

```sh
git clone <your-repo-url>
cd movie-watchlist-bot
```

### 2. Configure environment

```sh
cp .env.docker.example .env.docker.secret
```

Edit `.env.docker.secret` and fill in:
- `LLM_API_KEY` — your Qwen/LLM API key
- `LLM_API_MODEL` — model name (e.g. `qwen-plus`)
- `NANOBOT_ACCESS_KEY` — any random string for auth

### 3. Start the stack

```sh
docker compose up --build -d
```

### 4. Use the app

- **Swagger UI:** http://localhost:42002/docs — add movies directly via API
- **Nanobot Chat:** http://localhost:8080 — talk to the agent in natural language

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/movies/` | List all movies |
| POST | `/movies/` | Add a movie |
| PUT | `/movies/{id}` | Update a movie (title, genre, watched) |
| DELETE | `/movies/{id}` | Remove a movie |
| GET | `/movies/{id}` | Get movie details |

## Project Structure

```
movie-watchlist-bot/
├── backend/                # FastAPI + SQLAlchemy + PostgreSQL
│   ├── src/movie_backend/
│   ├── Dockerfile
│   └── pyproject.toml
├── nanobot/                # Nanobot agent
│   ├── workspace/          # SOUL.md, skills, memory
│   ├── entrypoint.py
│   ├── Dockerfile
│   └── pyproject.toml
├── mcp/                    # MCP servers
│   └── mcp-movies/         # Movie watchlist tools
├── nanobot-websocket-channel/
│   ├── nanobot-channel-protocol/
│   ├── nanobot-webchat/
│   └── mcp-webchat/
├── docker-compose.yml
├── .env.docker.example
└── pyproject.toml          # Root workspace (MCP packages)
```
