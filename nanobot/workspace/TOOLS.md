# Tool Usage Notes

## Movie Tools (mcp-movies)

- `add_movie` — Add a movie to the watchlist. Requires title, optionally genre and year.
- `list_movies` — Get all movies. Supports filtering by `watched` status.
- `get_movie` — Get details of a specific movie by ID.
- `update_movie` — Update a movie (title, genre, notes, watched status).
- `delete_movie` — Remove a movie from the list.
- `search_movies` — Search movies by title, genre, or notes.
- `get_movies_by_genre` — Get all movies of a specific genre.
- `get_unwatched_movies` — Get all movies not yet watched.

## Tips

- Always check the watchlist before suggesting — recommend from what the user actually saved.
- When the user says "I'm in the mood for [genre]", use `get_movies_by_genre` first, then `get_unwatched_movies` to filter.
- When the user says "what should I watch?", use `get_unwatched_movies` and pick one to recommend with enthusiasm.
- When the user says "mark it as watched", use `update_movie` with `watched=true`.
