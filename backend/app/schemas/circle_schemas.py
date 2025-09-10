from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum as PyEnum

# ---- Enumerations ----
class MemberRole(str, PyEnum):
    OWNER = "owner"
    ADMIN = "admin" 
    MEMBER = "member"

class MemberStatus(str, PyEnum):
    INVITED = "invited"
    ACTIVE = "active"
    INACTIVE = "inactive"

# ---- Base Schemas ----
class CircleBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    is_private: bool = False

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Circle name cannot be empty')
        return v.strip()

class CircleCreate(CircleBase):
    pass

class CircleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    is_private: Optional[bool] = None

    @validator('name')
    def name_must_be_valid(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Circle name cannot be empty')
        return v.strip() if v else v

class CircleResponse(CircleBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    member_count: Optional[int] = None

    class Config:
        from_attributes = True  # allow ORM -> Pydantic


class CircleMemberBase(BaseModel):
    role: MemberRole = MemberRole.MEMBER
    status: MemberStatus = MemberStatus.ACTIVE

class CircleMemberCreate(CircleMemberBase):
    user_id: int
    
class CircleMemberInvite(BaseModel):
    user_id: int
    role: MemberRole = MemberRole.MEMBER
    
class CircleMemberUpdate(BaseModel):
    role: Optional[MemberRole] = None
    status: Optional[MemberStatus] = None

class CircleMemberResponse(CircleMemberBase):
    id: int
    circle_id: int
    user_id: int
    joined_at: datetime
    invited_by: Optional[int] = None
    
    class Config:
        from_attributes = True
        
class CircleMemberDetailResponse(CircleMemberResponse):
    user: Dict[str, Any]  # Will include user details like username, etc.
    
class CircleDetailResponse(CircleResponse):
    owner: Dict[str, Any]  # Will include owner username, etc.
    members: List[CircleMemberDetailResponse] = []
    
class CircleListResponse(BaseModel):
    circles: List[CircleResponse]
    total: int
    skip: int
    limit: int
