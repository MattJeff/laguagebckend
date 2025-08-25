from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class WordAnalyzeRequest(BaseModel):
    word: str
    context: str
    userId: str
    source: str = "netflix"


class WordAnalyzeResponse(BaseModel):
    word: str
    translation: str
    definition: str
    difficulty: str
    part_of_speech: str
    synonyms: List[str]
    examples: List[str]
    pronunciation: str
    frequency: str


class WordBase(BaseModel):
    word: str
    translation: str
    definition: Optional[str] = None
    context: Optional[str] = None
    source: str = "netflix"


class WordCreate(WordBase):
    pass


class WordUpdate(BaseModel):
    translation: Optional[str] = None
    definition: Optional[str] = None
    mastery_level: Optional[float] = None


class Word(WordBase):
    id: int
    user_id: int
    part_of_speech: Optional[str] = None
    difficulty: Optional[str] = None
    pronunciation: Optional[str] = None
    frequency: Optional[str] = None
    synonyms: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    times_seen: int
    times_correct: int
    mastery_level: float
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
