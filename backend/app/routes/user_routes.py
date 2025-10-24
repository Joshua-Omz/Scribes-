"""User routes.

This module defines API routes for user management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.schemas.user_schemas import (
    UserResponse,
    UserUpdate,
    UserProfileResponse,
    UserListResponse,
    UserStatsResponse,
    ChangePasswordRequest,
    UserSearchRequest
)
from app.services.user_service import (
    get_user_service,
    get_user_profile_service,
    update_user_service,
    delete_user_service,
    change_password_service,
    search_users_service,
    get_user_stats_service,
    get_recent_users_service,
    deactivate_user_service,
    activate_user_service
)
from app.security.jwt import get_current_user

# Create router
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get the current authenticated user's detailed profile with statistics.

    Args:
        db: Database session
        current_user: Current user data from token

    Returns:
        UserProfileResponse: The user's detailed profile data
    """
    user_id = current_user.get("sub")
    return get_user_profile_service(db, user_id)


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update the current authenticated user's profile.

    Args:
        user_data: Updated user data
        db: Database session
        current_user: Current user data from token

    Returns:
        UserResponse: The updated user data
    """
    user_id = current_user.get("sub")
    return update_user_service(db, user_id, user_data)


@router.post("/me/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Change the current user's password.

    Args:
        password_data: Password change data
        db: Database session
        current_user: Current user data from token

    Returns:
        dict: Success message
    """
    user_id = current_user.get("sub")
    change_password_service(db, user_id, password_data)
    return {"detail": "Password changed successfully"}


@router.delete("/me")
async def delete_current_user_account(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete the current authenticated user's account.

    Args:
        db: Database session
        current_user: Current user data from token

    Returns:
        dict: Success message
    """
    user_id = current_user.get("sub")
    delete_user_service(db, user_id)
    return {"detail": "User account deleted successfully"}


@router.post("/me/deactivate")
async def deactivate_current_user_account(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deactivate the current authenticated user's account.

    Args:
        db: Database session
        current_user: Current user data from token

    Returns:
        UserResponse: The deactivated user data
    """
    user_id = current_user.get("sub")
    return deactivate_user_service(db, user_id)


@router.get("/stats", response_model=UserStatsResponse)
async def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get comprehensive user statistics (admin feature).

    Args:
        db: Database session
        current_user: Current user data from token

    Returns:
        UserStatsResponse: User statistics
    """
    # TODO: Add admin permission check
    return get_user_stats_service(db)


@router.get("/recent", response_model=List[UserResponse])
async def get_recent_users(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of recent users to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get recently registered users (admin feature).

    Args:
        limit: Maximum number of users to return
        db: Database session
        current_user: Current user data from token

    Returns:
        List[UserResponse]: List of recent users
    """
    # TODO: Add admin permission check
    return get_recent_users_service(db, limit)


@router.get("/search", response_model=UserListResponse)
async def search_users(
    query: Optional[str] = Query(None, description="Search query for username, email, or full name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_superuser: Optional[bool] = Query(None, description="Filter by superuser status"),
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of users to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Search and filter users (admin feature).

    Args:
        query: Search query
        is_active: Filter by active status
        is_superuser: Filter by superuser status
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        current_user: Current user data from token

    Returns:
        UserListResponse: Paginated list of users
    """
    # TODO: Add admin permission check
    return search_users_service(db, query, is_active, is_superuser, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a user by ID (admin feature).

    Args:
        user_id: ID of the user to retrieve
        db: Database session
        current_user: Current user data from token

    Returns:
        UserResponse: The user data
    """
    # TODO: Add admin permission check
    return get_user_service(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a user by ID (admin feature).

    Args:
        user_id: ID of the user to update
        user_data: Updated user data
        db: Database session
        current_user: Current user data from token

    Returns:
        UserResponse: The updated user data
    """
    # TODO: Add admin permission check
    return update_user_service(db, user_id, user_data)


@router.delete("/{user_id}")
async def delete_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a user by ID (admin feature).

    Args:
        user_id: ID of the user to delete
        db: Database session
        current_user: Current user data from token

    Returns:
        dict: Success message
    """
    # TODO: Add admin permission check
    delete_user_service(db, user_id)
    return {"detail": "User deleted successfully"}


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Activate a user account by ID (admin feature).

    Args:
        user_id: ID of the user to activate
        db: Database session
        current_user: Current user data from token

    Returns:
        UserResponse: The activated user data
    """
    # TODO: Add admin permission check
    return activate_user_service(db, user_id)


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Deactivate a user account by ID (admin feature).

    Args:
        user_id: ID of the user to deactivate
        db: Database session
        current_user: Current user data from token

    Returns:
        UserResponse: The deactivated user data
    """
    # TODO: Add admin permission check
    return deactivate_user_service(db, user_id)
