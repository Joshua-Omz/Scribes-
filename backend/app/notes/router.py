from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..core.database import get_db
from ..auth.dependencies import get_current_user
from ..users import schemas as user_schemas
from . import schemas, crud

router = APIRouter()

@router.get("/", response_model=schemas.NoteList)
async def get_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notes, total = crud.get_notes(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        search=search,
        tags=tags
    )
    
    return schemas.NoteList(
        notes=notes,
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )

@router.post("/", response_model=schemas.Note, status_code=status.HTTP_201_CREATED)
async def create_note(
    note: schemas.NoteCreate,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_note(db=db, note=note, user_id=current_user.id)

@router.get("/{note_id}", response_model=schemas.Note)
async def get_note(
    note_id: int,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = crud.get_note(db=db, note_id=note_id, user_id=current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note

@router.put("/{note_id}", response_model=schemas.Note)
async def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = crud.update_note(
        db=db,
        note_id=note_id,
        note_update=note_update,
        user_id=current_user.id
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = crud.delete_note(db=db, note_id=note_id, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

@router.get("/tags/", response_model=List[schemas.Tag])
async def get_tags(
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_tags(db=db)

@router.get("/reminders/", response_model=List[schemas.Note])
async def get_notes_with_reminders(
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_notes_with_reminders(db=db, user_id=current_user.id)

@router.post("/{note_id}/ai-paraphrase")
async def generate_ai_paraphrase(
    note_id: int,
    current_user: user_schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = crud.get_note(db=db, note_id=note_id, user_id=current_user.id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # TODO: Implement AI paraphrasing using OpenAI or similar service
    # This is a placeholder for the AI integration
    ai_summary = f"AI-generated summary for: {note.title[:50]}..."
    
    # For now, we'll just return the placeholder without updating the note
    # In a real implementation, this would call the AI service and update the note
    
    return {"ai_summary": ai_summary, "note_id": note_id}