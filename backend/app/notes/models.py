from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

# Association table for many-to-many relationship between notes and tags
note_tags = Table(
    'note_tags',
    Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=True)
    is_private = Column(Boolean, default=False)
    reminder_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    scripture_references = relationship("ScriptureReference", back_populates="note", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")

class ScriptureReference(Base):
    __tablename__ = "scripture_references"

    id = Column(Integer, primary_key=True, index=True)
    book = Column(String, nullable=False)
    chapter = Column(Integer, nullable=False)
    verse_start = Column(Integer, nullable=False)
    verse_end = Column(Integer, nullable=True)
    text = Column(Text, nullable=True)
    
    # Foreign key to note
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    
    # Relationship
    note = relationship("Note", back_populates="scripture_references")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    color = Column(String, nullable=True)  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    notes = relationship("Note", secondary=note_tags, back_populates="tags")