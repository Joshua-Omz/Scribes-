"""Reminder routes.

This module defines API routes for reminder management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas.reminder_schemas import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    ReminderListResponse,
    ReminderSearchRequest
)
from app.services.reminder_service import (
    create_reminder_service,
    get_reminder_service,
    get_user_reminders_service,
    update_reminder_service,
    delete_reminder_service,
    cancel_reminder_service,
    get_upcoming_reminders_service
)
from app.security.jwt import get_current_user

# Create router
router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.post("/", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new reminder.

    Args:
        reminder_data: Reminder creation data
        db: Database session
        current_user: Current authenticated user

    Returns:
        ReminderResponse: The created reminder data
    """
    user_id = current_user.get("sub")
    return create_reminder_service(db, reminder_data, user_id)


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific reminder by ID.

    Args:
        reminder_id: ID of the reminder to retrieve
        db: Database session
        current_user: Current authenticated user

    Returns:
        ReminderResponse: The reminder data

    Raises:
        HTTPException: If reminder not found or access denied
    """
    user_id = current_user.get("sub")
    return get_reminder_service(db, reminder_id, user_id)


@router.get("/", response_model=ReminderListResponse)
async def get_user_reminders(
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, sent, cancelled"),
    skip: int = Query(0, ge=0, description="Number of reminders to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of reminders to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get user's reminders with optional filtering and pagination.

    Args:
        status_filter: Optional status filter
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        ReminderListResponse: Paginated list of reminders
    """
    user_id = current_user.get("sub")
    reminders = get_user_reminders_service(db, user_id, status_filter, skip, limit)

    # Get total count for pagination info
    from app.db.repositories.reminder_repository import get_reminders_count_by_user
    total = get_reminders_count_by_user(db, user_id, status_filter)

    return ReminderListResponse(
        reminders=reminders,
        total=total,
        skip=skip,
        limit=limit,
        status_filter=status_filter
    )


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: int,
    update_data: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing reminder.

    Args:
        reminder_id: ID of the reminder to update
        update_data: Updated reminder data
        db: Database session
        current_user: Current authenticated user

    Returns:
        ReminderResponse: The updated reminder data

    Raises:
        HTTPException: If reminder not found or access denied
    """
    user_id = current_user.get("sub")
    return update_reminder_service(db, reminder_id, update_data, user_id)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a reminder.

    Args:
        reminder_id: ID of the reminder to delete
        db: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If reminder not found or access denied
    """
    user_id = current_user.get("sub")
    delete_reminder_service(db, reminder_id, user_id)
    return {"detail": "Reminder deleted successfully"}


@router.post("/{reminder_id}/cancel", response_model=ReminderResponse)
async def cancel_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a pending reminder.

    Args:
        reminder_id: ID of the reminder to cancel
        db: Database session
        current_user: Current authenticated user

    Returns:
        ReminderResponse: The cancelled reminder data

    Raises:
        HTTPException: If reminder not found, access denied, or not pending
    """
    user_id = current_user.get("sub")
    return cancel_reminder_service(db, reminder_id, user_id)


@router.get("/upcoming/list", response_model=List[ReminderResponse])
async def get_upcoming_reminders(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of upcoming reminders to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get upcoming pending reminders for the current user.

    Args:
        limit: Maximum number of reminders to return
        db: Database session
        current_user: Current authenticated user

    Returns:
        List[ReminderResponse]: List of upcoming reminders
    """
    user_id = current_user.get("sub")
    return get_upcoming_reminders_service(db, user_id, limit)
