"""Models for notes.   

This module defines the database models for notes."""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime  
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func

from app.db.database import Base    


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    preacher = Column(String(100), nullable=True)  # optional field
    tags = Column(String(255), nullable=True)      # comma-separated tags
    scripture_refs = Column(String(255), nullable=True)  # e.g. "John 3:16, Matt 5:9"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship (optional but good for queries later)
    user = relationship("User", back_populates="notes")
    reminders = relationship("Reminder", back_populates="note", cascade="all, delete")
    shared_circles = relationship("CircleNote", back_populates="note", cascade="all, delete")