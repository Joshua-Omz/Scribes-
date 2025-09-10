"""User service.

This module provides business logic for user management operations.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
import logging

from app.db.repositories import user_repository, note_repository, reminder_repository
from app.schemas.user_schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfileResponse,
    UserListResponse,
    UserStatsResponse,
    ChangePasswordRequest
)
from app.services.auth import get_password_hash, verify_password
from app.models.user_model import User

# Configure logging
logger = logging.getLogger(__name__)


def create_user_service(db: Session, user_data: UserCreate) -> User:
    """Create a new user with comprehensive validation and security checks."""
    try:
        # Check if user with email exists
        if user_repository.check_email_exists(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if user with username exists
        if user_repository.check_username_exists(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Hash the password
        hashed_password = get_password_hash(user_data.password)

        logger.info(f"Creating new user: {user_data.username}")
        return user_repository.create_user(db, user_data, hashed_password)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user {user_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


def get_user_service(db: Session, user_id: int) -> User:
    """Retrieve a user with proper error handling."""
    try:
        user = user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


def get_user_profile_service(db: Session, user_id: int) -> UserProfileResponse:
    """Get detailed user profile with statistics."""
    try:
        user = user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get user statistics
        notes_count = note_repository.get_notes_count_by_user(db, user_id)
        reminders_count = reminder_repository.get_reminders_count_by_user(db, user_id)
        active_reminders_count = reminder_repository.get_reminders_count_by_user(
            db, user_id, status_filter="pending"
        )

        # Convert to response schema
        user_dict = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "notes_count": notes_count,
            "reminders_count": reminders_count,
            "active_reminders_count": active_reminders_count
        }

        return UserProfileResponse(**user_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile"
        )


def update_user_service(db: Session, user_id: int, update_data: UserUpdate) -> User:
    """Update a user with validation and security checks."""
    try:
        # Get current user
        user = user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Validate email uniqueness if email is being updated
        if update_data.email and update_data.email != user.email:
            if user_repository.check_email_exists(db, update_data.email, exclude_user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

        # Validate username uniqueness if username is being updated
        if update_data.username and update_data.username != user.username:
            if user_repository.check_username_exists(db, update_data.username, exclude_user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Hash password if provided
        if update_data.password:
            update_data.password = get_password_hash(update_data.password)

        logger.info(f"Updating user {user_id}")
        updated_user = user_repository.update_user(db, user_id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )

        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


def delete_user_service(db: Session, user_id: int) -> None:
    """Delete a user with proper authorization and cleanup."""
    try:
        # Get user to verify existence
        user = user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"Deleting user {user_id} ({user.username})")
        success = user_repository.delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


def change_password_service(db: Session, user_id: int, password_data: ChangePasswordRequest) -> None:
    """Change a user's password with validation."""
    try:
        # Get user
        user = user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Hash new password
        hashed_password = get_password_hash(password_data.new_password)

        # Update password
        success = user_repository.update_user_password(db, user_id, hashed_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        logger.info(f"Password changed for user {user_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


def search_users_service(db: Session, query: Optional[str] = None, is_active: Optional[bool] = None,
                        is_superuser: Optional[bool] = None, skip: int = 0, limit: int = 50) -> UserListResponse:
    """Search and filter users with pagination."""
    try:
        # Validate pagination parameters
        if skip < 0 or limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid pagination parameters"
            )

        users = user_repository.search_users(db, query, is_active, is_superuser, skip, limit)
        total = user_repository.get_users_count(db, query, is_active, is_superuser)

        return UserListResponse(
            users=users,
            total=total,
            skip=skip,
            limit=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )


def get_user_stats_service(db: Session) -> UserStatsResponse:
    """Get comprehensive user statistics."""
    try:
        stats = user_repository.get_user_stats(db)
        return UserStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error retrieving user statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user statistics"
        )


def get_recent_users_service(db: Session, limit: int = 10) -> List[UserResponse]:
    """Get recently registered users."""
    try:
        if limit <= 0 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid limit parameter"
            )

        users = user_repository.get_recent_users(db, limit)
        return users

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving recent users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recent users"
        )


def deactivate_user_service(db: Session, user_id: int) -> User:
    """Deactivate a user account."""
    try:
        user = user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already deactivated"
            )

        logger.info(f"Deactivating user {user_id}")
        success = user_repository.deactivate_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate user"
            )

        # Refresh user data
        user = user_repository.get_user_by_id(db, user_id)
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate user"
        )


def activate_user_service(db: Session, user_id: int) -> User:
    """Activate a user account."""
    try:
        user = user_repository.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already active"
            )

        logger.info(f"Activating user {user_id}")
        success = user_repository.activate_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to activate user"
            )

        # Refresh user data
        user = user_repository.get_user_by_id(db, user_id)
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user"
        )
