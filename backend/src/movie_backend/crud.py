from sqlalchemy.orm import Session

from . import models, schemas


def get_movies(db: Session, skip: int = 0, limit: int = 100, watched: bool | None = None):
    query = db.query(models.Movie)
    if watched is not None:
        query = query.filter(models.Movie.watched == watched)
    return query.order_by(models.Movie.created_at.desc()).offset(skip).limit(limit).all()


def get_movie(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def create_movie(db: Session, movie: schemas.MovieCreate):
    db_movie = models.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def update_movie(db: Session, movie_id: int, movie: schemas.MovieUpdate):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        return None
    update_data = movie.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie


def delete_movie(db: Session, movie_id: int):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not db_movie:
        return None
    db.delete(db_movie)
    db.commit()
    return db_movie


def search_movies(db: Session, query: str):
    """Search movies by title, genre, or notes."""
    search_pattern = f"%{query}%"
    return (
        db.query(models.Movie)
        .filter(
            models.Movie.title.ilike(search_pattern)
            | models.Movie.genre.ilike(search_pattern)
            | models.Movie.notes.ilike(search_pattern)
        )
        .all()
    )


def get_movies_by_genre(db: Session, genre: str):
    """Get all movies matching a genre (case-insensitive)."""
    return (
        db.query(models.Movie)
        .filter(models.Movie.genre.ilike(f"%{genre}%"))
        .order_by(models.Movie.created_at.desc())
        .all()
    )


def get_unwatched_movies(db: Session):
    """Get all movies not yet watched."""
    return (
        db.query(models.Movie)
        .filter(models.Movie.watched == False)
        .order_by(models.Movie.created_at.desc())
        .all()
    )
