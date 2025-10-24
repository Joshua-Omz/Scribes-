from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator

class NoteBase(BaseModel):
    """Base schema for notes with common attributes."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    preacher: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(default_factory=list)
    scripture_tags: Optional[List[str]] = Field(default_factory=list)

    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

    @validator('tags', 'scripture_tags', each_item=True)
    def sanitize_tags(cls, v):
        return v.strip() if v else v

class NoteCreate(NoteBase):
    """Schema for creating a new note."""
    pass

class NoteUpdate(BaseModel):
    """Schema for updating an existing note."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    preacher: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    scripture_tags: Optional[List[str]] = None

    @validator('title')
    def title_must_not_be_empty_if_provided(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else v

    @validator('content')
    def content_must_not_be_empty_if_provided(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Content cannot be empty')
        return v.strip() if v else v

    @validator('tags', 'scripture_tags', each_item=True)
    def sanitize_tags(cls, v):
        return v.strip() if v else v

class NoteResponse(BaseModel):
    """Schema for note response data."""
    id: int
    user_id: int
    title: str
    content: str
    preacher: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    scripture_tags: Optional[List[str]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('tags', pre=True, always=True)
    def parse_tags(cls, v):
        if isinstance(v, str) and v:
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        elif isinstance(v, list):
            return v
        return []

    @validator('scripture_tags', pre=True, always=True)
    def parse_scripture_tags(cls, v):
        if isinstance(v, str) and v:
            return [tag.strip() for tag in v.split(',') if tag.strip()]
        elif isinstance(v, list):
            return v
        return []

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class NoteListResponse(BaseModel):
    """Schema for paginated note list response."""
    notes: List[NoteResponse]
    total: int
    skip: int
    limit: int

class NoteSearchRequest(BaseModel):
    """Schema for note search request."""
    query: str = Field(..., min_length=2, max_length=100)
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)

class CircleNotesResponse(BaseModel):
    """Schema for notes in a circle response."""
    notes: List[NoteResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        from_attributes = True