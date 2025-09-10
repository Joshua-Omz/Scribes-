from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone
import logging

from app.db.repositories import reminder_repository, note_repository
from app.schemas.reminder_schemas import ReminderCreate, ReminderUpdate, ReminderResponse
from app.models.reminder_model import Reminder

# Configure logging
logger = logging.getLogger(__name__)

def create_reminder_service(db: Session, reminder_data: ReminderCreate, user_id: int) -> Reminder:
    """Create a new reminder with comprehensive validation and security checks."""
    try:
        # Validate reminder_id format
        if reminder_data.note_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid note ID"
            )

        # Verify that the note exists and belongs to the user
        note = note_repository.get_note_by_user(db, reminder_data.note_id, user_id)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or access denied"
            )

        # Validate scheduled time
        if reminder_data.scheduled_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reminder cannot be scheduled in the past"
            )

        # Check for reasonable future date (not too far ahead)
        max_future_days = 365  # 1 year
        if (reminder_data.scheduled_at - datetime.now(timezone.utc)).days > max_future_days:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reminder cannot be scheduled more than {max_future_days} days in the future"
            )

        # Check for duplicate reminders (same note, same time)
        existing_reminder = db.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.note_id == reminder_data.note_id,
            Reminder.scheduled_at == reminder_data.scheduled_at,
            Reminder.status == "pending"
        ).first()

        if existing_reminder:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A reminder for this note at this time already exists"
            )

        logger.info(f"Creating reminder for user {user_id}, note {reminder_data.note_id}")
        return reminder_repository.create_reminder(db, reminder_data, user_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating reminder for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create reminder"
        )

def get_reminder_service(db: Session, reminder_id: int, user_id: int) -> Reminder:
    """Retrieve a reminder with proper authorization and error handling."""
    try:
        if reminder_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reminder ID"
            )

        reminder = reminder_repository.get_reminder_by_user(db, reminder_id, user_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found or access denied"
            )

        return reminder

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving reminder {reminder_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reminder"
        )

def get_user_reminders_service(db: Session, user_id: int, status_filter: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Reminder]:
    """Retrieve user reminders with optional filtering and pagination."""
    try:
        # Validate pagination parameters
        if skip < 0 or limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pagination parameters"
            )

        # Validate status filter
        valid_statuses = ["pending", "sent", "cancelled"]
        if status_filter and status_filter not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter. Must be one of: {', '.join(valid_statuses)}"
            )

        reminders = reminder_repository.get_user_reminders_paginated(
            db, user_id, status_filter, skip, limit
        )
        return reminders

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving reminders for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reminders"
        )

def update_reminder_service(db: Session, reminder_id: int, update_data: ReminderUpdate, user_id: int) -> Reminder:
    """Update a reminder with validation and security checks."""
    try:
        if reminder_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reminder ID"
            )

        # Get and validate ownership
        reminder = reminder_repository.get_reminder_by_user(db, reminder_id, user_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found or access denied"
            )

        # Validate status if provided
        if update_data.status and update_data.status not in ["pending", "sent", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be: pending, sent, or cancelled"
            )

        # Validate scheduled time if provided
        if update_data.scheduled_at:
            if update_data.scheduled_at <= datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reminder cannot be scheduled in the past"
                )

            # Check if reminder is already sent
            if reminder.status == "sent":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot update scheduled time for sent reminders"
                )

        logger.info(f"Updating reminder {reminder_id} for user {user_id}")
        return reminder_repository.update_reminder(db, reminder, update_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reminder {reminder_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reminder"
        )

def delete_reminder_service(db: Session, reminder_id: int, user_id: int) -> None:
    """Delete a reminder with proper authorization."""
    try:
        if reminder_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reminder ID"
            )

        # Get and validate ownership
        reminder = reminder_repository.get_reminder_by_user(db, reminder_id, user_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found or access denied"
            )

        # Prevent deletion of sent reminders (optional business rule)
        if reminder.status == "sent":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete sent reminders"
            )

        logger.info(f"Deleting reminder {reminder_id} for user {user_id}")
        reminder_repository.delete_reminder(db, reminder)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting reminder {reminder_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete reminder"
        )

def cancel_reminder_service(db: Session, reminder_id: int, user_id: int) -> Reminder:
    """Cancel a pending reminder."""
    try:
        if reminder_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reminder ID"
            )

        # Get and validate ownership
        reminder = reminder_repository.get_reminder_by_user(db, reminder_id, user_id)
        if not reminder:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reminder not found or access denied"
            )

        if reminder.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel reminder with status: {reminder.status}"
            )

        # Update status to cancelled
        update_data = ReminderUpdate(status="cancelled")
        logger.info(f"Cancelling reminder {reminder_id} for user {user_id}")
        return reminder_repository.update_reminder(db, reminder, update_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling reminder {reminder_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel reminder"
        )

def get_upcoming_reminders_service(db: Session, user_id: int, limit: int = 10) -> List[Reminder]:
    """Get upcoming pending reminders for a user."""
    try:
        if limit <= 0 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid limit parameter"
            )

        reminders = reminder_repository.get_upcoming_reminders(db, user_id, limit)
        return reminders

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving upcoming reminders for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve upcoming reminders"
        )
