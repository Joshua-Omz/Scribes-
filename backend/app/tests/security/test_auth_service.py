"""Tests for authentication service.

This module contains tests for the authentication service functionality.
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.auth import (
    verify_password,
    get_password_hash,
    authenticate_user,
    create_user,
    create_tokens_for_user
)
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate


def test_password_hashing():
    """Test password hashing and verification."""
    # Create password hash
    password = "testpassword"
    hashed = get_password_hash(password)
    
    # Verify hash is different from original
    assert hashed != password
    
    # Verify password validates against hash
    assert verify_password(password, hashed)
    
    # Verify wrong password fails
    assert not verify_password("wrongpassword", hashed)


def test_authenticate_user():
    """Test user authentication."""
    # Mock database session
    db = MagicMock(spec=Session)
    
    # Mock user with correct password
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    
    # Configure mock to return user
    db.query.return_value.filter.return_value.first.return_value = user
    
    # Test successful authentication
    authenticated_user = authenticate_user(db, "testuser", "testpassword")
    assert authenticated_user is not None
    assert authenticated_user.username == "testuser"
    
    # Test failed authentication with wrong password
    db.query.return_value.filter.return_value.first.return_value = user
    authenticated_user = authenticate_user(db, "testuser", "wrongpassword")
    assert authenticated_user is None
    
    # Test failed authentication with nonexistent user
    db.query.return_value.filter.return_value.first.return_value = None
    authenticated_user = authenticate_user(db, "nonexistent", "testpassword")
    assert authenticated_user is None


def test_create_user():
    """Test user creation."""
    # Mock database session
    db = MagicMock(spec=Session)
    
    # Configure mock for email check
    db.query.return_value.filter.return_value.first.side_effect = [None, None]
    
    # Create user data
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword",
        full_name="Test User"
    )
    
    # Test user creation
    new_user = create_user(db, user_data)
    
    # Verify user was added to database
    assert db.add.called
    assert db.commit.called
    assert db.refresh.called
    
    # Test exception when email already exists
    db.query.return_value.filter.return_value.first.side_effect = [MagicMock(), None]
    with pytest.raises(HTTPException) as excinfo:
        create_user(db, user_data)
    assert excinfo.value.status_code == 400
    assert "email" in excinfo.value.detail.lower()
    
    # Test exception when username already exists
    db.query.return_value.filter.return_value.first.side_effect = [None, MagicMock()]
    with pytest.raises(HTTPException) as excinfo:
        create_user(db, user_data)
    assert excinfo.value.status_code == 400
    assert "username" in excinfo.value.detail.lower()


def test_create_tokens_for_user():
    """Test token creation for user."""
    # Mock user
    user = MagicMock()
    user.id = 1
    user.username = "testuser"
    
    # Create tokens
    tokens = create_tokens_for_user(user)
    
    # Verify tokens were created
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"
