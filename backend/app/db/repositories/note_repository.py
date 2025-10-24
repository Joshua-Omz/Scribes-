from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from app.models.notes_models import Note
from app.schemas.notes_schemas import NoteCreate, NoteUpdate

def create_note(db: Session, note_data: NoteCreate, user_id: int) -> Note:
    """Create a new note with proper field mapping."""
    note = Note(
        title=note_data.title,
        content=note_data.content,
        preacher=getattr(note_data, 'preacher', None),
        tags=getattr(note_data, 'tags', None),  # This will be a comma-separated string
        scripture_refs=getattr(note_data, 'scripture_tags', None),  # Map to scripture_refs
        user_id=user_id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def get_note_by_user(db: Session, note_id: int, user_id: int) -> Optional[Note]:
    """Get a specific note for a user."""
    return db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()

def get_notes_by_user(db: Session, user_id: int) -> List[Note]:
    """Get all notes for a user."""
    return db.query(Note).filter(Note.user_id == user_id).all()

def get_notes_by_user_paginated(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    """Get notes for a user with pagination."""
    return db.query(Note).filter(
        Note.user_id == user_id
    ).offset(skip).limit(limit).all()

def update_note(db: Session, note: Note, update_data: NoteUpdate) -> Note:
    """Update a note with validation and security checks."""
    # Define allowed fields to prevent mass assignment vulnerabilities
    allowed_fields = {
        'title', 'content', 'preacher', 'tags', 'scripture_refs'
    }

    # Get the update data as a dictionary
    update_dict = update_data.dict(exclude_unset=True)

    # Filter out any fields that aren't in our allowed list
    filtered_updates = {k: v for k, v in update_dict.items() if k in allowed_fields}

    # Handle field mapping for scripture_tags -> scripture_refs
    if 'scripture_tags' in update_dict:
        filtered_updates['scripture_refs'] = update_dict['scripture_tags']

    # Apply updates
    for field, value in filtered_updates.items():
        setattr(note, field, value)

    db.commit()
    db.refresh(note)
    return note

def delete_note(db: Session, note: Note) -> None:
    """Delete a note."""
    db.delete(note)
    db.commit()

def search_notes_by_user(db: Session, user_id: int, query: str, skip: int = 0, limit: int = 50) -> List[Note]:
    """Search notes by title or content for a specific user."""
    search_term = f"%{query}%"
    return db.query(Note).filter(
        Note.user_id == user_id,
        or_(
            Note.title.ilike(search_term),
            Note.content.ilike(search_term),
            Note.tags.ilike(search_term),
            Note.scripture_refs.ilike(search_term)
        )
    ).offset(skip).limit(limit).all()

def get_notes_count_by_user(db: Session, user_id: int) -> int:
    """Get the total count of notes for a user."""
    return db.query(func.count(Note.id)).filter(Note.user_id == user_id).scalar()

def get_recent_notes_by_user(db: Session, user_id: int, limit: int = 10) -> List[Note]:
    """Get the most recent notes for a user."""
    return db.query(Note).filter(
        Note.user_id == user_id
    ).order_by(Note.updated_at.desc()).limit(limit).all() 
