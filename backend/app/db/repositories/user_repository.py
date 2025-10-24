"""User repository.

This module provides functions for accessing user data in the database.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from datetime import datetime, timedelta

from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db: Database session
        user_id: The ID of the user to get

    Returns:
        Optional[User]: The user or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """
    Get a user by username.

    Args:
        db: Database session
        username: The username to search for

    Returns:
        Optional[User]: The user or None if not found
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        db: Database session
        email: The email to search for

    Returns:
        Optional[User]: The user or None if not found
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username_or_email(db: Session, username_or_email: str) -> Optional[User]:
    """
    Get a user by username or email.

    Args:
        db: Database session
        username_or_email: The username or email to search for

    Returns:
        Optional[User]: The user or None if not found
    """
    return db.query(User).filter(
        or_(User.username == username_or_email, User.email == username_or_email)
    ).first()


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    List users with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List[User]: List of users
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_data: UserCreate, hashed_password: str) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user_data: User creation data
        hashed_password: Pre-hashed password

    Returns:
        User: The created user
    """
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """
    Update a user.

    Args:
        db: Database session
        user_id: The ID of the user to update
        user_data: User update data

    Returns:
        Optional[User]: The updated user or None if not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None

    # Update user fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user.

    Args:
        db: Database session
        user_id: The ID of the user to delete

    Returns:
        bool: True if the user was deleted, False if not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True


def search_users(db: Session, query: Optional[str] = None, is_active: Optional[bool] = None,
                is_superuser: Optional[bool] = None, skip: int = 0, limit: int = 50) -> List[User]:
    """
    Search and filter users.

    Args:
        db: Database session
        query: Search query for username, email, or full name
        is_active: Filter by active status
        is_superuser: Filter by superuser status
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        List[User]: List of matching users
    """
    q = db.query(User)

    if query:
        search_filter = f"%{query}%"
        q = q.filter(
            or_(
                User.username.ilike(search_filter),
                User.email.ilike(search_filter),
                User.full_name.ilike(search_filter)
            )
        )

    if is_active is not None:
        q = q.filter(User.is_active == is_active)

    if is_superuser is not None:
        q = q.filter(User.is_superuser == is_superuser)

    return q.offset(skip).limit(limit).all()


def get_users_count(db: Session, query: Optional[str] = None, is_active: Optional[bool] = None,
                   is_superuser: Optional[bool] = None) -> int:
    """
    Get the count of users matching the search criteria.

    Args:
        db: Database session
        query: Search query for username, email, or full name
        is_active: Filter by active status
        is_superuser: Filter by superuser status

    Returns:
        int: Number of matching users
    """
    q = db.query(func.count(User.id))

    if query:
        search_filter = f"%{query}%"
        q = q.filter(
            or_(
                User.username.ilike(search_filter),
                User.email.ilike(search_filter),
                User.full_name.ilike(search_filter)
            )
        )

    if is_active is not None:
        q = q.filter(User.is_active == is_active)

    if is_superuser is not None:
        q = q.filter(User.is_superuser == is_superuser)

    return q.scalar()


def get_user_stats(db: Session) -> Dict[str, Any]:
    """
    Get comprehensive user statistics.

    Args:
        db: Database session

    Returns:
        Dict[str, Any]: User statistics
    """
    # Total users
    total_users = db.query(func.count(User.id)).scalar()

    # Active users
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()

    # Inactive users
    inactive_users = db.query(func.count(User.id)).filter(User.is_active == False).scalar()

    # Superuser count
    superuser_count = db.query(func.count(User.id)).filter(User.is_superuser == True).scalar()

    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_registrations = db.query(func.count(User.id)).filter(
        User.created_at >= thirty_days_ago
    ).scalar()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "superuser_count": superuser_count,
        "recent_registrations": recent_registrations
    }


def get_recent_users(db: Session, limit: int = 10) -> List[User]:
    """
    Get recently registered users.

    Args:
        db: Database session
        limit: Maximum number of users to return

    Returns:
        List[User]: List of recently registered users
    """
    return db.query(User).order_by(User.created_at.desc()).limit(limit).all()


def check_username_exists(db: Session, username: str, exclude_user_id: Optional[int] = None) -> bool:
    """
    Check if a username already exists.

    Args:
        db: Database session
        username: Username to check
        exclude_user_id: User ID to exclude from check (for updates)

    Returns:
        bool: True if username exists, False otherwise
    """
    query = db.query(User).filter(User.username == username)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    return query.first() is not None


def check_email_exists(db: Session, email: str, exclude_user_id: Optional[int] = None) -> bool:
    """
    Check if an email already exists.

    Args:
        db: Database session
        email: Email to check
        exclude_user_id: User ID to exclude from check (for updates)

    Returns:
        bool: True if email exists, False otherwise
    """
    query = db.query(User).filter(User.email == email)
    if exclude_user_id:
        query = query.filter(User.id != exclude_user_id)
    return query.first() is not None


def update_user_password(db: Session, user_id: int, hashed_password: str) -> bool:
    """
    Update a user's password.

    Args:
        db: Database session
        user_id: The ID of the user
        hashed_password: The new hashed password

    Returns:
        bool: True if password was updated, False if user not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db_user.hashed_password = hashed_password
    db.commit()
    return True


def deactivate_user(db: Session, user_id: int) -> bool:
    """
    Deactivate a user account.

    Args:
        db: Database session
        user_id: The ID of the user to deactivate

    Returns:
        bool: True if user was deactivated, False if not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db_user.is_active = False
    db.commit()
    return True


def activate_user(db: Session, user_id: int) -> bool:
    """
    Activate a user account.

    Args:
        db: Database session
        user_id: The ID of the user to activate

    Returns:
        bool: True if user was activated, False if not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False

    db_user.is_active = True
    db.commit()
    return True
