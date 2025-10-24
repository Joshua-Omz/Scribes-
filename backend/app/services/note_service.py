from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
import logging

from app.db.repositories import note_repository
from app.schemas.notes_schemas import NoteCreate, NoteUpdate, NoteResponse
from app.models.notes_models import Note

# Configure logging
logger = logging.getLogger(__name__)

def _split_csv(value: Optional[str]) -> List[str]:
    """Turn 'a,b,c' into ['a','b','c'] with trimming; empty -> []."""
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]

def _format_note_for_response(note: Note) -> dict:
    """
    Convert SQLAlchemy Note -> dict shaped for NoteResponse:
    - tags/scripture_tags become lists
    - created_at/updated_at pass through
    """
    # Some codebases name the DB column 'scripture_refs' (model) but schema uses 'scripture_tags'
    scripture_csv = getattr(note, "scripture_refs", None) or getattr(note, "scripture_tags", None)

    return {
        "id": note.id,
        "user_id": note.user_id,
        "title": note.title,
        "content": note.content,
        "preacher": note.preacher,
        "tags": _split_csv(getattr(note, "tags", None)),
        "scripture_tags": _split_csv(scripture_csv),
        "created_at": note.created_at,
        "updated_at": note.updated_at,
    }

def create_note_service(db: Session, note_data: NoteCreate, user_id: int) -> Note:
    """Create a new note for a user with validation and error handling."""
    try:
        # Validate input data
        if not note_data.title or not note_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Note title cannot be empty"
            )

        if not note_data.content or not note_data.content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Note content cannot be empty"
            )

        # Sanitize and validate tags
        if note_data.tags:
            # Convert list to comma-separated string for storage
            sanitized_tags = ",".join([tag.strip() for tag in note_data.tags if tag.strip()])
            note_data.tags = sanitized_tags if sanitized_tags else None

        if note_data.scripture_tags:
            # Convert list to comma-separated string for storage
            sanitized_scripture_tags = ",".join([tag.strip() for tag in note_data.scripture_tags if tag.strip()])
            note_data.scripture_tags = sanitized_scripture_tags if sanitized_scripture_tags else None

        logger.info(f"Creating note for user {user_id}: {note_data.title}")
        created = note_repository.create_note(db, note_data, user_id)
        return _format_note_for_response(created)

    except Exception as e:
        logger.error(f"Error creating note for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create note"
        )

def get_note_service(db: Session, note_id: int, user_id: int) -> Note:
    """Retrieve a note if it belongs to the user with proper error handling."""
    try:
        if note_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid note ID"
            )

        note = note_repository.get_note_by_user(db, note_id, user_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or access denied"
            )

        return _format_note_for_response(note)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving note {note_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve note"
        )

def get_notes_service(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    """Retrieve all notes for a user with pagination."""
    try:
        if skip < 0 or limit <= 0 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pagination parameters"
            )

        notes = note_repository.get_notes_by_user_paginated(db, user_id, skip, limit)
        return [_format_note_for_response(n) for n in notes]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving notes for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notes"
        )

def update_note_service(db: Session, note_id: int, update_data: NoteUpdate, user_id: int) -> Note:
    """Update a note if it belongs to the user with validation."""
    try:
        if note_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid note ID"
            )

        # Check if note exists and belongs to user
        note = note_repository.get_note_by_user(db, note_id, user_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or access denied"
            )

        # Validate update data
        if update_data.title is not None and not update_data.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Note title cannot be empty"
            )

        if update_data.content is not None and not update_data.content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Note content cannot be empty"
            )

        # Sanitize tags if provided
        if update_data.tags is not None:
            if update_data.tags:
                sanitized_tags = ",".join([tag.strip() for tag in update_data.tags if tag.strip()])
                update_data.tags = sanitized_tags if sanitized_tags else None
            else:
                update_data.tags = None

        if update_data.scripture_tags is not None:
            if update_data.scripture_tags:
                sanitized_scripture_tags = ",".join([tag.strip() for tag in update_data.scripture_tags if tag.strip()])
                update_data.scripture_tags = sanitized_scripture_tags if sanitized_scripture_tags else None
            else:
                update_data.scripture_tags = None

        logger.info(f"Updating note {note_id} for user {user_id}")
        updated = note_repository.update_note(db, note, update_data)
        return _format_note_for_response(updated)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note {note_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update note"
        )

def delete_note_service(db: Session, note_id: int, user_id: int) -> None:
    """Delete a note if it belongs to the user."""
    try:
        if note_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid note ID"
            )

        # Check if note exists and belongs to user
        note = note_repository.get_note_by_user(db, note_id, user_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or access denied"
            )

        logger.info(f"Deleting note {note_id} for user {user_id}")
        note_repository.delete_note(db, note)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note {note_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note"
        )

def search_notes_service(db: Session, user_id: int, query: str, skip: int = 0, limit: int = 50) -> List[Note]:
    """Search notes by title or content."""
    try:
        if not query or not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query cannot be empty"
            )

        if len(query.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query must be at least 2 characters long"
            )

        if skip < 0 or limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pagination parameters"
            )

        notes = note_repository.search_notes_by_user(db, user_id, query.strip(), skip, limit)
        return [_format_note_for_response(n) for n in notes]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching notes for user {user_id} with query '{query}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search notes"
        )
