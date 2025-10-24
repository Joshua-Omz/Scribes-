from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timezone
from app.models.reminder_model import Reminder
from app.schemas.reminder_schemas import ReminderCreate, ReminderUpdate

def create_reminder(db: Session, reminder_data: ReminderCreate, user_id: int) -> Reminder:
    """Create a new reminder with proper field mapping."""
    reminder = Reminder(
        user_id=user_id,
        note_id=reminder_data.note_id,
        scheduled_at=reminder_data.scheduled_at,
        status="pending"  # Default status
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

def get_reminder(db: Session, reminder_id: int) -> Optional[Reminder]:
    """Get a reminder by ID (internal use - doesn't check ownership)."""
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()

def get_reminder_by_user(db: Session, reminder_id: int, user_id: int) -> Optional[Reminder]:
    """Get a reminder by ID with user ownership validation."""
    return db.query(Reminder).filter(
        and_(
            Reminder.id == reminder_id,
            Reminder.user_id == user_id
        )
    ).first()

def get_user_reminders(db: Session, user_id: int) -> List[Reminder]:
    """Get all reminders for a user."""
    return db.query(Reminder).filter(Reminder.user_id == user_id).all()

def get_user_reminders_paginated(db: Session, user_id: int, status_filter: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Reminder]:
    """Get user reminders with optional status filtering and pagination."""
    query = db.query(Reminder).filter(Reminder.user_id == user_id)

    if status_filter:
        query = query.filter(Reminder.status == status_filter)

    return query.offset(skip).limit(limit).all()

def update_reminder(db: Session, reminder: Reminder, update_data: ReminderUpdate) -> Reminder:
    """Update a reminder with security validation."""
    # Define allowed fields to prevent mass assignment vulnerabilities
    allowed_fields = {'scheduled_at', 'status'}

    # Get the update data as a dictionary
    update_dict = update_data.dict(exclude_unset=True)

    # Filter out any fields that aren't in our allowed list
    filtered_updates = {k: v for k, v in update_dict.items() if k in allowed_fields}

    # Apply updates
    for field, value in filtered_updates.items():
        setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)
    return reminder

def delete_reminder(db: Session, reminder: Reminder) -> None:
    """Delete a reminder."""
    db.delete(reminder)
    db.commit()

def get_upcoming_reminders(db: Session, user_id: int, limit: int = 10) -> List[Reminder]:
    """Get upcoming pending reminders for a user."""
    now = datetime.now(timezone.utc)
    return db.query(Reminder).filter(
        and_(
            Reminder.user_id == user_id,
            Reminder.status == "pending",
            Reminder.scheduled_at > now
        )
    ).order_by(Reminder.scheduled_at.asc()).limit(limit).all()

def get_overdue_reminders(db: Session, user_id: Optional[int] = None) -> List[Reminder]:
    """Get overdue pending reminders (for background processing)."""
    now = datetime.now(timezone.utc)
    query = db.query(Reminder).filter(
        and_(
            Reminder.status == "pending",
            Reminder.scheduled_at <= now
        )
    )

    if user_id:
        query = query.filter(Reminder.user_id == user_id)

    return query.all()

def update_reminder_status(db: Session, reminder_id: int, new_status: str) -> bool:
    """Update reminder status (for background processing)."""
    valid_statuses = ["pending", "sent", "cancelled"]
    if new_status not in valid_statuses:
        return False

    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        return False

    reminder.status = new_status
    db.commit()
    return True

def get_reminders_count_by_user(db: Session, user_id: int, status_filter: Optional[str] = None) -> int:
    """Get the total count of reminders for a user."""
    query = db.query(Reminder).filter(Reminder.user_id == user_id)

    if status_filter:
        query = query.filter(Reminder.status == status_filter)

    return query.count()

def get_reminders_by_note(db: Session, note_id: int, user_id: int) -> List[Reminder]:
    """Get all reminders for a specific note (with user validation)."""
    return db.query(Reminder).filter(
        and_(
            Reminder.note_id == note_id,
            Reminder.user_id == user_id
        )
    ).all()

def bulk_update_reminder_status(db: Session, reminder_ids: List[int], new_status: str) -> int:
    """Bulk update reminder status (for background processing)."""
    valid_statuses = ["pending", "sent", "cancelled"]
    if new_status not in valid_statuses:
        return 0

    # Update only pending reminders to prevent overwriting sent/cancelled ones
    result = db.query(Reminder).filter(
        and_(
            Reminder.id.in_(reminder_ids),
            Reminder.status == "pending"
        )
    ).update({"status": new_status})

    db.commit()
    return result
