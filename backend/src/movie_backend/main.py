from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from . import crud, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Watchlist API", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/movies/", response_model=list[schemas.MovieResponse])
def list_movies(
    skip: int = 0,
    limit: int = 100,
    watched: bool | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_movies(db, skip=skip, limit=limit, watched=watched)


@app.get("/movies/search", response_model=list[schemas.MovieResponse])
def search_movies(q: str, db: Session = Depends(get_db)):
    return crud.search_movies(db, q)


@app.get("/movies/genre/{genre}", response_model=list[schemas.MovieResponse])
def movies_by_genre(genre: str, db: Session = Depends(get_db)):
    return crud.get_movies_by_genre(db, genre)


@app.get("/movies/unwatched", response_model=list[schemas.MovieResponse])
def unwatched_movies(db: Session = Depends(get_db)):
    return crud.get_unwatched_movies(db)


@app.get("/movies/{movie_id}", response_model=schemas.MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@app.post("/movies/", response_model=schemas.MovieResponse, status_code=201)
def add_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    return crud.create_movie(db, movie)


@app.put("/movies/{movie_id}", response_model=schemas.MovieResponse)
def update_movie(movie_id: int, movie: schemas.MovieUpdate, db: Session = Depends(get_db)):
    updated = crud.update_movie(db, movie_id, movie)
    if not updated:
        raise HTTPException(status_code=404, detail="Movie not found")
    return updated


@app.delete("/movies/{movie_id}", response_model=schemas.MovieResponse)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_movie(db, movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Movie not found")
    return deleted
