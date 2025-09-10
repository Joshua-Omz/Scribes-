from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from ..core.database import get_db
from ..core.security import create_access_token
from ..core.config import settings
from ..users import crud, schemas as user_schemas
from ..auth.dependencies import get_current_user
from . import schemas

router = APIRouter()

@router.post("/register", response_model=schemas.TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.RegisterRequest,
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_create = user_schemas.UserCreate(
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )
    
    db_user = crud.create_user(db, user_create)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "email": db_user.email,
            "name": db_user.name,
            "is_premium": db_user.is_premium,
            "created_at": db_user.created_at.isoformat(),
            "profile_image_url": db_user.profile_image_url
        }
    }

@router.post("/login", response_model=schemas.TokenResponse)
async def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    user = crud.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_premium": user.is_premium,
            "created_at": user.created_at.isoformat(),
            "profile_image_url": user.profile_image_url
        }
    }

@router.post("/refresh", response_model=schemas.TokenResponse)
async def refresh_token(
    current_user: user_schemas.User = Depends(get_current_user)
):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "is_premium": current_user.is_premium,
            "created_at": current_user.created_at.isoformat(),
            "profile_image_url": current_user.profile_image_url
        }
    }

@router.get("/me", response_model=user_schemas.User)
async def get_current_user_info(
    current_user: user_schemas.User = Depends(get_current_user)
):
    return current_user