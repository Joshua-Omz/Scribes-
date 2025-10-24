from fastapi import APIRouter, Depends, status, Query, Path, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.db.database import get_db
from app.services import circle_service
from app.schemas.circle_schemas import (
    CircleCreate, CircleUpdate, CircleResponse, CircleDetailResponse, CircleListResponse,
    CircleMemberCreate, CircleMemberInvite, CircleMemberUpdate, CircleMemberResponse
)
from app.schemas.notes_schemas import NoteResponse, CircleNotesResponse
from app.security.jwt import get_current_user

# Create router with appropriate prefix and tags
router = APIRouter(prefix="/circles", tags=["Circles"])

# ---- Circle Endpoints ----
@router.post("/", response_model=CircleResponse, status_code=status.HTTP_201_CREATED)
async def create_circle(
    circle_data: CircleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new circle.
    
    Args:
        circle_data: Circle creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleResponse: The created circle
    """
    user_id = current_user.get("sub")
    return circle_service.create_circle_service(db, circle_data, user_id)

@router.get("/", response_model=CircleListResponse)
async def get_user_circles(
    skip: int = Query(0, ge=0, description="Number of circles to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of circles to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all circles where the current user is a member or owner.
    
    Args:
        skip: Number of circles to skip for pagination
        limit: Maximum number of circles to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleListResponse: List of circles with pagination information
    """
    user_id = current_user.get("sub")
    return circle_service.get_user_circles_service(db, user_id, skip, limit)

@router.get("/{circle_id}", response_model=CircleResponse)
async def get_circle(
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific circle by ID.
    
    Args:
        circle_id: ID of the circle to retrieve
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleResponse: The circle data
        
    Raises:
        HTTPException: If circle not found or access denied
    """
    user_id = current_user.get("sub")
    return circle_service.get_circle_service(db, circle_id, user_id)

@router.get("/{circle_id}/detail", response_model=CircleDetailResponse)
async def get_circle_detail(
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a circle including members.
    
    Args:
        circle_id: ID of the circle to retrieve
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleDetailResponse: The circle details with members
        
    Raises:
        HTTPException: If circle not found or access denied
    """
    user_id = current_user.get("sub")
    return circle_service.get_circle_detail_service(db, circle_id, user_id)

@router.put("/{circle_id}", response_model=CircleResponse)
async def update_circle(
    circle_data: CircleUpdate,
    circle_id: int = Path(..., ge=1, description="The ID of the circle to update"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a circle's information.
    
    Args:
        circle_data: Updated circle data
        circle_id: ID of the circle to update
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleResponse: The updated circle
        
    Raises:
        HTTPException: If circle not found or not authorized
    """
    user_id = current_user.get("sub")
    return circle_service.update_circle_service(db, circle_id, circle_data, user_id)

@router.delete("/{circle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_circle(
    circle_id: int = Path(..., ge=1, description="The ID of the circle to delete"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a circle.
    
    Args:
        circle_id: ID of the circle to delete
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If circle not found or not authorized
    """
    user_id = current_user.get("sub")
    circle_service.delete_circle_service(db, circle_id, user_id)
    return {"detail": "Circle deleted successfully"}

# ---- Circle Member Endpoints ----
@router.post("/{circle_id}/members", response_model=CircleMemberResponse)
async def add_member(
    member_data: CircleMemberCreate,
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a member to a circle.
    
    Args:
        member_data: Member data to add
        circle_id: ID of the circle
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleMemberResponse: The added member
        
    Raises:
        HTTPException: If circle not found or not authorized
    """
    user_id = current_user.get("sub")
    return circle_service.add_member_service(db, circle_id, member_data, user_id)

@router.post("/{circle_id}/invite", response_model=CircleMemberResponse)
async def invite_member(
    invite_data: CircleMemberInvite,
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Invite a member to a circle.
    
    Args:
        invite_data: Invitation data
        circle_id: ID of the circle
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleMemberResponse: The created invitation
        
    Raises:
        HTTPException: If circle not found or not authorized
    """
    user_id = current_user.get("sub")
    return circle_service.invite_member_service(db, circle_id, invite_data, user_id)

@router.get("/{circle_id}/members", response_model=Dict[str, Any])
async def get_circle_members(
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    skip: int = Query(0, ge=0, description="Number of members to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of members to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all members of a circle.
    
    Args:
        circle_id: ID of the circle
        skip: Number of members to skip for pagination
        limit: Maximum number of members to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Dict containing members list and pagination info
        
    Raises:
        HTTPException: If circle not found or access denied
    """
    user_id = current_user.get("sub")
    return circle_service.get_circle_members_service(db, circle_id, user_id, skip, limit)

@router.put("/{circle_id}/members/{user_id}", response_model=CircleMemberResponse)
async def update_member(
    update_data: CircleMemberUpdate,
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    user_id: int = Path(..., ge=1, description="The ID of the user to update"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a member's role or status.
    
    Args:
        update_data: Updated member data
        circle_id: ID of the circle
        user_id: ID of the user to update
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleMemberResponse: The updated member
        
    Raises:
        HTTPException: If circle not found, member not found, or not authorized
    """
    current_user_id = current_user.get("sub")
    return circle_service.update_member_service(db, circle_id, user_id, update_data, current_user_id)

@router.delete("/{circle_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    user_id: int = Path(..., ge=1, description="The ID of the user to remove"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a member from a circle.
    
    Args:
        circle_id: ID of the circle
        user_id: ID of the user to remove
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If circle not found, member not found, or not authorized
    """
    current_user_id = current_user.get("sub")
    circle_service.remove_member_service(db, circle_id, user_id, current_user_id)
    return {"detail": "Member removed successfully"}

# ---- Circle Notes Endpoints ----
@router.get("/{circle_id}/notes", response_model=CircleNotesResponse)
async def get_circle_notes(
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    skip: int = Query(0, ge=0, description="Number of notes to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of notes to return"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all notes shared with a circle.
    
    Args:
        circle_id: ID of the circle
        skip: Number of notes to skip for pagination
        limit: Maximum number of notes to return
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        CircleNotesResponse: Notes shared with the circle with pagination info
        
    Raises:
        HTTPException: If circle not found or access denied
    """
    current_user_id = current_user.get("sub")
    return circle_service.get_circle_notes_service(db, circle_id, current_user_id, skip, limit)

@router.post("/{circle_id}/notes/{note_id}", status_code=status.HTTP_201_CREATED, response_model=NoteResponse)
async def add_note_to_circle(
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    note_id: int = Path(..., ge=1, description="The ID of the note to add"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Share a note with a circle.
    
    Args:
        circle_id: ID of the circle
        note_id: ID of the note to share
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        NoteResponse: The complete note object that was shared
        
    Raises:
        HTTPException: If circle not found, note not found, or not authorized
    """
    current_user_id = current_user.get("sub")
    return circle_service.add_note_to_circle_service(db, circle_id, note_id, current_user_id)

@router.delete("/{circle_id}/notes/{note_id}", status_code=status.HTTP_200_OK)
async def remove_note_from_circle(
    circle_id: int = Path(..., ge=1, description="The ID of the circle"),
    note_id: int = Path(..., ge=1, description="The ID of the note to remove"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove a shared note from a circle.
    
    Args:
        circle_id: ID of the circle
        note_id: ID of the note to remove
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        A success message
        
    Raises:
        HTTPException: If circle not found, note not found, or not authorized
    """
    current_user_id = current_user.get("sub")
    return circle_service.remove_note_from_circle_service(db, circle_id, note_id, current_user_id)
