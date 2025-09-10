from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ScriptureReferenceBase(BaseModel):
    book: str
    chapter: int
    verse_start: int
    verse_end: Optional[int] = None
    text: Optional[str] = None

class ScriptureReferenceCreate(ScriptureReferenceBase):
    pass

class ScriptureReference(ScriptureReferenceBase):
    id: int
    note_id: int
    
    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str
    color: Optional[str] = None

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class NoteBase(BaseModel):
    title: str
    content: str
    is_private: bool = False
    reminder_date: Optional[datetime] = None

class NoteCreate(NoteBase):
    tags: Optional[List[str]] = []
    scripture_references: Optional[List[ScriptureReferenceCreate]] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_private: Optional[bool] = None
    reminder_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    scripture_references: Optional[List[ScriptureReferenceCreate]] = None

class Note(NoteBase):
    id: int
    user_id: int
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tags: List[Tag] = []
    scripture_references: List[ScriptureReference] = []
    
    class Config:
        from_attributes = True

class NoteList(BaseModel):
    notes: List[Note]
    total: int
    page: int
    per_page: int