"""Refresh token repository.

This module provides functions for accessing refresh token data in the database.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


def create_refresh_token(db: Session, token: str, user_id: int, expires_at: datetime) -> RefreshToken:
    """
    Create a new refresh token.
    
    Args:
        db: Database session
        token: The refresh token string
        user_id: The ID of the token owner
        expires_at: When the token expires
        
    Returns:
        RefreshToken: The created token record
    """
    token_record = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(token_record)
    db.commit()
    db.refresh(token_record)
    return token_record


def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """
    Get a refresh token by value.
    
    Args:
        db: Database session
        token: The refresh token string to search for
        
    Returns:
        Optional[RefreshToken]: The token record or None if not found
    """
    return db.query(RefreshToken).filter(RefreshToken.token == token).first()


def validate_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """
    Validate a refresh token.
    
    Args:
        db: Database session
        token: The refresh token string to validate
        
    Returns:
        Optional[RefreshToken]: The valid token record or None if invalid
    """
    token_record = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    return token_record


def revoke_refresh_token(db: Session, token: str) -> bool:
    """
    Revoke a refresh token.
    
    Args:
        db: Database session
        token: The refresh token string to revoke
        
    Returns:
        bool: True if the token was found and revoked, False otherwise
    """
    token_record = get_refresh_token(db, token)
    if not token_record:
        return False
        
    token_record.revoked = True
    db.commit()
    return True


def revoke_all_user_tokens(db: Session, user_id: int) -> int:
    """
    Revoke all refresh tokens for a user.
    
    Args:
        db: Database session
        user_id: The ID of the token owner
        
    Returns:
        int: The number of tokens revoked
    """
    result = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()
    return result


def delete_expired_tokens(db: Session) -> int:
    """
    Delete expired tokens from the database.
    
    Args:
        db: Database session
        
    Returns:
        int: The number of tokens deleted
    """
    result = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.utcnow()
    ).delete()
    
    db.commit()
    return result
