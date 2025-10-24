"""Notes routes.

This module defines API routes for note management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas.notes_schemas import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteListResponse,
    NoteSearchRequest
)
from app.services.note_service import (
    create_note_service,
    get_note_service,
    get_notes_service,
    update_note_service,
    delete_note_service,
    search_notes_service,
    _format_note_for_response
)
from app.security.jwt import get_current_user

# Create router
router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new note.

    Args:
        note_data: Note creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        NoteResponse: The created note data
    """
    user_id = current_user.get("sub")
    return create_note_service(db, note_data, user_id)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific note by ID.

    Args:
        note_id: ID of the note to retrieve
        db: Database session
        current_user: Current authenticated user

    Returns:
        NoteResponse: The note data

    Raises:
        HTTPException: If note not found or access denied
    """
    user_id = current_user.get("sub")
    return get_note_service(db, note_id, user_id)


@router.get("/", response_model=NoteListResponse)
async def get_notes(
    skip: int = Query(0, ge=0, description="Number of notes to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of notes to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's notes with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        NoteListResponse: Paginated list of notes
    """
    user_id = current_user.get("sub")
    notes = get_notes_service(db, user_id, skip, limit)

    # Get total count for pagination info
    from app.db.repositories.note_repository import get_notes_count_by_user
    total = get_notes_count_by_user(db, user_id)

    return NoteListResponse(
        notes=notes,
        total=total,
        skip=skip,
        limit=limit
    )


@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: int,
    update_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing note.

    Args:
        note_id: ID of the note to update
        update_data: Updated note data
        db: Database session
        current_user: Current authenticated user

    Returns:
        NoteResponse: The updated note data

    Raises:
        HTTPException: If note not found or access denied
    """
    user_id = current_user.get("sub")
    return update_note_service(db, note_id, update_data, user_id)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a note.

    Args:
        note_id: ID of the note to delete
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If note not found or access denied
    """
    user_id = current_user.get("sub")
    delete_note_service(db, note_id, user_id)
    return {"detail": "Note deleted successfully"}


@router.post("/search", response_model=List[NoteResponse])
async def search_notes(
    search_request: NoteSearchRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Search notes by title, content, tags, or scripture references.

    Args:
        search_request: Search parameters including query, skip, and limit
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[NoteResponse]: List of matching notes
    """
    user_id = current_user.get("sub")
    return search_notes_service(
        db,
        user_id,
        search_request.query,
        search_request.skip,
        search_request.limit
    )


@router.get("/recent/list", response_model=List[NoteResponse])
async def get_recent_notes(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recent notes to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the most recent notes for the user.

    Args:
        limit: Maximum number of notes to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[NoteResponse]: List of recent notes
    """
    user_id = current_user.get("sub")
    from app.db.repositories.note_repository import get_recent_notes_by_user
    notes = get_recent_notes_by_user(db, user_id, limit)
    return [_format_note_for_response(n) for n in notes]
