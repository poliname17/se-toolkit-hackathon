from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = None
    notes: Optional[str] = Field("", max_length=500)


class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = None
    notes: Optional[str] = Field(None, max_length=500)
    watched: Optional[bool] = None


class MovieResponse(BaseModel):
    id: int
    title: str
    genre: Optional[str]
    year: Optional[int]
    notes: str
    watched: bool
    created_at: datetime

    class Config:
        from_attributes = True
