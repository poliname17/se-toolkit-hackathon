"""
MovieBot — a simple agent with MCP tools, exposed via WebSocket.
"""

import asyncio
import json
import os
import logging
import websockets
from openai import AsyncOpenAI
from websockets.server import serve

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

LLM_API_KEY = os.environ["LLM_API_KEY"]
LLM_API_BASE = os.environ.get("LLM_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_MODEL = os.environ.get("LLM_API_MODEL", "qwen-plus")
BACKEND_URL = os.environ.get("MOVIE_BACKEND_URL", "http://backend:8000")
HOST = os.environ.get("CHAT_HOST", "0.0.0.0")
PORT = int(os.environ.get("CHAT_PORT", "8765"))

client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)

SYSTEM_PROMPT = """You are MovieBot 🎬 — a friendly movie assistant.
You help users manage their movie watchlist and suggest what to watch.
Use the provided tools to interact with the backend.
Keep responses concise and conversational.
"""

# --- MCP-style tools (simple HTTP wrappers) ---

async def tool_list_movies(watched=None):
    """List all movies in the watchlist. watched can be 'true', 'false', or omitted."""
    async with httpx.AsyncClient(base_url=BACKEND_URL) as c:
        params = {}
        if watched in ("true", "false"):
            params["watched"] = watched == "true"
        resp = await c.get("/movies/", params=params)
        movies = resp.json()
    if not movies:
        return "Your watchlist is empty."
    lines = ["Your watchlist:"]
    for m in movies:
        status = "✓ watched" if m["watched"] else "○ unwatched"
        year = f" ({m['year']})" if m.get("year") else ""
        genre = f" — {m['genre']}" if m.get("genre") else ""
        lines.append(f"  {m['id']}. {m['title']}{year}{genre} — {status}")
    return "\n".join(lines)

async def tool_add_movie(title, genre=None, year=None, notes=None):
    """Add a movie to the watchlist. title is required."""
    payload = {"title": title}
    if genre: payload["genre"] = genre
    if year: payload["year"] = year
    if notes: payload["notes"] = notes
    async with httpx.AsyncClient(base_url=BACKEND_URL) as c:
        resp = await c.post("/movies/", json=payload)
        m = resp.json()
    return f"Added: {m['title']} (ID: {m['id']})"

async def tool_update_movie(movie_id, watched=None, title=None, genre=None):
    """Update a movie. Provide movie_id and the fields to change."""
    payload = {}
    if watched is not None: payload["watched"] = watched
    if title: payload["title"] = title
    if genre: payload["genre"] = genre
    async with httpx.AsyncClient(base_url=BACKEND_URL) as c:
        resp = await c.put(f"/movies/{movie_id}", json=payload)
        if resp.status_code == 404:
            return f"Movie {movie_id} not found."
        m = resp.json()
    return f"Updated: {m['title']}"

async def tool_delete_movie(movie_id):
    """Delete a movie from the watchlist."""
    async with httpx.AsyncClient(base_url=BACKEND_URL) as c:
        resp = await c.delete(f"/movies/{movie_id}")
        if resp.status_code == 404:
            return f"Movie {movie_id} not found."
        m = resp.json()
    return f"Deleted: {m['title']}"

async def tool_search_movies(query):
    """Search movies by title, genre, or notes."""
    async with httpx.AsyncClient(base_url=BACKEND_URL) as c:
        resp = await c.get("/movies/search", params={"q": query})
        movies = resp.json()
    if not movies:
        return f"No movies matching '{query}'."
    lines = [f"Movies matching '{query}':"]
    for m in movies:
        status = "✓ watched" if m["watched"] else "○ unwatched"
        lines.append(f"  {m['id']}. {m['title']} — {status}")
    return "\n".join(lines)

async def tool_unwatched():
    """Get all unwatched movies. Use when user asks 'what should I watch?'."""
    async with httpx.AsyncClient(base_url=BACKEND_URL) as c:
        resp = await c.get("/movies/unwatched")
        movies = resp.json()
    if not movies:
        return "No unwatched movies — you've seen everything! 🎬"
    lines = ["Unwatched movies:"]
    for m in movies:
        year = f" ({m['year']})" if m.get("year") else ""
        genre = f" — {m['genre']}" if m.get("genre") else ""
        lines.append(f"  {m['id']}. {m['title']}{year}{genre}")
    return "\n".join(lines)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_movies",
            "description": "List all movies in the watchlist. Optionally filter by watched status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "watched": {"type": "string", "enum": ["true", "false"], "description": "Filter by watched status"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_movie",
            "description": "Add a movie to the watchlist. title is required.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Movie title"},
                    "genre": {"type": "string", "description": "Genre like Sci-Fi, Comedy, Drama"},
                    "year": {"type": "integer", "description": "Release year"},
                    "notes": {"type": "string", "description": "Personal notes"}
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_movie",
            "description": "Update a movie's fields. Must provide movie_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "movie_id": {"type": "integer", "description": "The movie ID"},
                    "watched": {"type": "boolean", "description": "Mark as watched"},
                    "title": {"type": "string"},
                    "genre": {"type": "string"}
                },
                "required": ["movie_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_movie",
            "description": "Delete a movie by its ID.",
            "parameters": {
                "type": "object",
                "properties": {"movie_id": {"type": "integer"}},
                "required": ["movie_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_movies",
            "description": "Search movies by title, genre, or notes.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search term"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "unwatched",
            "description": "Get all unwatched movies. Use when the user asks what they should watch.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]

TOOL_FUNCS = {
    "list_movies": lambda watched=None: tool_list_movies(watched),
    "add_movie": tool_add_movie,
    "update_movie": tool_update_movie,
    "delete_movie": tool_delete_movie,
    "search_movies": tool_search_movies,
    "unwatched": tool_unwatched,
}


async def handle_message(text):
    """Run one turn of the agent. Returns the assistant's reply."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]

    response = await client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
    )

    choice = response.choices[0]
    tool_calls = choice.message.tool_calls

    if tool_calls:
        for tc in tool_calls:
            func_name = tc.function.name
            args = json.loads(tc.function.arguments)
            logger.info(f"Tool call: {func_name}({args})")
            result = await TOOL_FUNCS[func_name](**args)
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tc],
            })
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})

        # Second turn — LLM generates final response
        response = await client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content or "Done."

    return choice.message.content or "I'm not sure what to say."


async def websocket_handler(ws, path):
    logger.info("Client connected")
    try:
        async for message in ws:
            try:
                data = json.loads(message)
                text = data.get("text", "")
                if not text:
                    continue
                logger.info(f"User: {text}")
                reply = await handle_message(text)
                logger.info(f"Bot: {reply}")
                await ws.send(json.dumps({"text": reply}))
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await ws.send(json.dumps({"text": f"Error: {e}"}))
    except websockets.ConnectionClosed:
        pass
    logger.info("Client disconnected")


async def main():
    logger.info(f"MovieBot starting on ws://{HOST}:{PORT}")
    async with serve(websocket_handler, HOST, PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
