from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    profile_image_url: Optional[str] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_premium: bool
    profile_image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass