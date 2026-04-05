from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from .database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    genre = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    notes = Column(String(500), nullable=True, default="")
    watched = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
