from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
from . import models, schemas

def get_notes(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 10,
    search: Optional[str] = None,
    tags: Optional[List[str]] = None
):
    query = db.query(models.Note).filter(models.Note.user_id == user_id)
    
    if search:
        query = query.filter(
            or_(
                models.Note.title.ilike(f"%{search}%"),
                models.Note.content.ilike(f"%{search}%")
            )
        )
    
    if tags:
        query = query.join(models.Note.tags).filter(models.Tag.name.in_(tags))
    
    total = query.count()
    notes = query.order_by(models.Note.updated_at.desc()).offset(skip).limit(limit).all()
    
    return notes, total

def get_note(db: Session, note_id: int, user_id: int):
    return db.query(models.Note).filter(
        and_(models.Note.id == note_id, models.Note.user_id == user_id)
    ).first()

def create_note(db: Session, note: schemas.NoteCreate, user_id: int):
    db_note = models.Note(
        title=note.title,
        content=note.content,
        is_private=note.is_private,
        reminder_date=note.reminder_date,
        user_id=user_id
    )
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Handle tags
    if note.tags:
        for tag_name in note.tags:
            tag = get_or_create_tag(db, tag_name)
            db_note.tags.append(tag)
    
    # Handle scripture references
    if note.scripture_references:
        for scripture_ref in note.scripture_references:
            db_scripture = models.ScriptureReference(
                **scripture_ref.dict(),
                note_id=db_note.id
            )
            db.add(db_scripture)
    
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, note_id: int, note_update: schemas.NoteUpdate, user_id: int):
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return None
    
    update_data = note_update.dict(exclude_unset=True, exclude={'tags', 'scripture_references'})
    for field, value in update_data.items():
        setattr(db_note, field, value)
    
    # Handle tags update
    if note_update.tags is not None:
        db_note.tags.clear()
        for tag_name in note_update.tags:
            tag = get_or_create_tag(db, tag_name)
            db_note.tags.append(tag)
    
    # Handle scripture references update
    if note_update.scripture_references is not None:
        # Clear existing references
        db.query(models.ScriptureReference).filter(
            models.ScriptureReference.note_id == note_id
        ).delete()
        
        # Add new references
        for scripture_ref in note_update.scripture_references:
            db_scripture = models.ScriptureReference(
                **scripture_ref.dict(),
                note_id=note_id
            )
            db.add(db_scripture)
    
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int, user_id: int):
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return False
    
    db.delete(db_note)
    db.commit()
    return True

def get_or_create_tag(db: Session, tag_name: str):
    tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
    if not tag:
        tag = models.Tag(name=tag_name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
    return tag

def get_tags(db: Session):
    return db.query(models.Tag).all()

def get_notes_with_reminders(db: Session, user_id: int):
    """Get notes that have upcoming reminders"""
    return db.query(models.Note).filter(
        and_(
            models.Note.user_id == user_id,
            models.Note.reminder_date.isnot(None)
        )
    ).order_by(models.Note.reminder_date).all()