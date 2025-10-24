"""JWT authentication implementation.

This module provides functions for creating, validating, and refreshing JWT tokens
used for authenticating users in the Scribes application.
"""
from jose import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings

# OAuth2 password bearer scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a new JWT access token.
    
    Args:
        data: The payload data to include in the token
        expires_delta: Optional expiration time, defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES
        
    Returns:
        str: JWT token string
    """
    to_encode = data.copy()
    
    # Convert user_id to string for JWT compatibility
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire, "token_type": "access"})
    
    # Create JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a new JWT refresh token with longer expiration time.
    
    Args:
        data: The payload data to include in the token
        
    Returns:
        str: JWT refresh token string
    """
    to_encode = data.copy()
    
    # Convert user_id to string for JWT compatibility
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    # Set longer expiration time for refresh token
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    
    # Create JWT refresh token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_REFRESH_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str, secret_key: str, is_refresh: bool = False) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: The JWT token to verify
        secret_key: The secret key used to decode the token
        is_refresh: Whether this is a refresh token verification
        
    Returns:
        Dict[str, Any]: The decoded payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Verify token type
        token_type = payload.get("token_type")
        expected_type = "refresh" if is_refresh else "access"
        
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {expected_type} token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert sub back to integer if it's a string representation of an integer
        if "sub" in payload and isinstance(payload["sub"], str) and payload["sub"].isdigit():
            payload["sub"] = int(payload["sub"])
            
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify an access token.
    
    Args:
        token: The access token to verify
        
    Returns:
        Dict[str, Any]: The decoded payload
    """
    return verify_token(token, settings.JWT_SECRET_KEY)


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    Verify a refresh token.
    
    Args:
        token: The refresh token to verify
        
    Returns:
        Dict[str, Any]: The decoded payload
    """
    return verify_token(token, settings.JWT_REFRESH_SECRET_KEY, is_refresh=True)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get the current authenticated user from the access token.
    
    Args:
        token: The access token from the request
        
    Returns:
        Dict[str, Any]: The user data from the token
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    payload = verify_access_token(token)
    return payload
