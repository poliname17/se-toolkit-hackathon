"""
MCP Server for Movie Watchlist tools.

Exposes tools that let the nanobot agent interact with the movie watchlist backend.
"""

import os
from mcp.server.fastmcp import FastMCP
import httpx

BACKEND_URL = os.environ.get("MOVIE_BACKEND_URL", "http://localhost:8000")

mcp = FastMCP("movie-watchlist")


def _client() -> httpx.Client:
    return httpx.Client(base_url=BACKEND_URL, timeout=10.0)


@mcp.tool()
def list_movies(watched: bool | None = None) -> str:
    """List all movies in the watchlist. Optionally filter by watched status (true/false).
    
    Args:
        watched: If true, return only watched movies. If false, return only unwatched.
                 If omitted, return all movies.
    """
    params = {}
    if watched is not None:
        params["watched"] = str(watched).lower()
    
    with _client() as c:
        resp = c.get("/movies/", params=params)
        resp.raise_for_status()
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


@mcp.tool()
def add_movie(title: str, genre: str | None = None, year: int | None = None, notes: str | None = None) -> str:
    """Add a movie to the watchlist.
    
    Args:
        title: The movie title (required).
        genre: The genre (e.g. 'Sci-Fi', 'Comedy', 'Drama').
        year: The release year.
        notes: Optional personal notes (e.g. 'recommended by Sarah').
    """
    payload = {"title": title}
    if genre:
        payload["genre"] = genre
    if year:
        payload["year"] = year
    if notes:
        payload["notes"] = notes
    
    with _client() as c:
        resp = c.post("/movies/", json=payload)
        resp.raise_for_status()
        movie = resp.json()
    
    year_str = f" ({movie['year']})" if movie.get("year") else ""
    genre_str = f" [{movie['genre']}]" if movie.get("genre") else ""
    return f"Added: {movie['title']}{year_str}{genre_str} (ID: {movie['id']})"


@mcp.tool()
def get_movie(movie_id: int) -> str:
    """Get details of a specific movie by its ID.
    
    Args:
        movie_id: The movie ID.
    """
    with _client() as c:
        resp = c.get(f"/movies/{movie_id}")
        if resp.status_code == 404:
            return f"Movie with ID {movie_id} not found."
        resp.raise_for_status()
        movie = resp.json()
    
    lines = [
        f"Title: {movie['title']}",
        f"ID: {movie['id']}",
    ]
    if movie.get("year"):
        lines.append(f"Year: {movie['year']}")
    if movie.get("genre"):
        lines.append(f"Genre: {movie['genre']}")
    lines.append(f"Watched: {'Yes' if movie['watched'] else 'No'}")
    if movie.get("notes"):
        lines.append(f"Notes: {movie['notes']}")
    
    return "\n".join(lines)


@mcp.tool()
def update_movie(movie_id: int, title: str | None = None, genre: str | None = None,
                 year: int | None = None, notes: str | None = None, watched: bool | None = None) -> str:
    """Update a movie in the watchlist. Only provide fields you want to change.
    
    Args:
        movie_id: The movie ID.
        title: New title.
        genre: New genre.
        year: New year.
        notes: New notes.
        watched: Set watched status (true or false).
    """
    payload = {}
    if title is not None:
        payload["title"] = title
    if genre is not None:
        payload["genre"] = genre
    if year is not None:
        payload["year"] = year
    if notes is not None:
        payload["notes"] = notes
    if watched is not None:
        payload["watched"] = watched
    
    with _client() as c:
        resp = c.put(f"/movies/{movie_id}", json=payload)
        if resp.status_code == 404:
            return f"Movie with ID {movie_id} not found."
        resp.raise_for_status()
        movie = resp.json()
    
    return f"Updated: {movie['title']} (ID: {movie['id']})"


@mcp.tool()
def delete_movie(movie_id: int) -> str:
    """Delete a movie from the watchlist.
    
    Args:
        movie_id: The movie ID.
    """
    with _client() as c:
        resp = c.delete(f"/movies/{movie_id}")
        if resp.status_code == 404:
            return f"Movie with ID {movie_id} not found."
        resp.raise_for_status()
        movie = resp.json()
    
    return f"Deleted: {movie['title']} (ID: {movie['id']})"


@mcp.tool()
def search_movies(query: str) -> str:
    """Search movies in the watchlist by title, genre, or notes.
    
    Args:
        query: The search term.
    """
    with _client() as c:
        resp = c.get("/movies/search", params={"q": query})
        resp.raise_for_status()
        movies = resp.json()
    
    if not movies:
        return f"No movies matching '{query}'."
    
    lines = [f"Movies matching '{query}':"]
    for m in movies:
        status = "✓ watched" if m["watched"] else "○ unwatched"
        year = f" ({m['year']})" if m.get("year") else ""
        genre = f" — {m['genre']}" if m.get("genre") else ""
        lines.append(f"  {m['id']}. {m['title']}{year}{genre} — {status}")
    
    return "\n".join(lines)


@mcp.tool()
def get_movies_by_genre(genre: str) -> str:
    """Get all movies in a specific genre.
    
    Args:
        genre: The genre to filter by (e.g. 'Sci-Fi', 'Comedy', 'Drama').
    """
    with _client() as c:
        resp = c.get(f"/movies/genre/{genre}")
        resp.raise_for_status()
        movies = resp.json()
    
    if not movies:
        return f"No movies in genre '{genre}'."
    
    lines = [f"Movies in '{genre}':"]
    for m in movies:
        status = "✓ watched" if m["watched"] else "○ unwatched"
        year = f" ({m['year']})" if m.get("year") else ""
        lines.append(f"  {m['id']}. {m['title']}{year} — {status}")
    
    return "\n".join(lines)


@mcp.tool()
def get_unwatched_movies() -> str:
    """Get all movies that haven't been watched yet. Use this when the user asks 'what should I watch?'"""
    with _client() as c:
        resp = c.get("/movies/unwatched")
        resp.raise_for_status()
        movies = resp.json()
    
    if not movies:
        return "No unwatched movies — you've seen everything on your list! 🎬"
    
    lines = ["Unwatched movies (pick one to watch!):"]
    for m in movies:
        year = f" ({m['year']})" if m.get("year") else ""
        genre = f" — {m['genre']}" if m.get("genre") else ""
        lines.append(f"  {m['id']}. {m['title']}{year}{genre}")
    
    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
