from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional, Tuple
import logging

from app.db.repositories import circle_repository, user_repository
from app.models.notes_models import Note
from app.schemas.circle_schemas import (
    CircleCreate, CircleUpdate, CircleMemberCreate, 
    CircleMemberInvite, CircleMemberUpdate, CircleResponse,
    CircleDetailResponse, CircleMemberResponse, CircleListResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# ---- Circle Services ----
def create_circle_service(db: Session, circle_data: CircleCreate, owner_id: int) -> Dict[str, Any]:
    """Create a new circle with the given owner."""
    try:
        circle = circle_repository.create_circle(db, circle_data, owner_id)
        circle_data = circle_repository.get_circle_with_member_count(db, circle.id)
        return circle_data
    except Exception as e:
        logger.error(f"Error creating circle: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create circle: {str(e)}"
        )

def get_circle_service(db: Session, circle_id: int, current_user_id: int) -> Dict[str, Any]:
    """Get a circle by ID if the user is authorized."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )

        # Check access permission
        if circle.is_private and not _check_circle_access(db, circle, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this circle"
            )
            
        circle_data = circle_repository.get_circle_with_member_count(db, circle_id)
        return circle_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve circle"
        )

def get_circle_detail_service(db: Session, circle_id: int, current_user_id: int) -> CircleDetailResponse:
    """Get detailed circle information including members if user is authorized."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Circle not found"
            )
            
        # Check access permission
        if circle.is_private and not _check_circle_access(db, circle, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this circle"
            )
        
        # Get circle data with member count
        circle_data = circle_repository.get_circle_with_member_count(db, circle_id)
        
        # Get owner details
        owner = user_repository.get_user_by_id(db, circle.owner_id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Circle owner not found"
            )
        
        owner_data = {
            "id": owner.id,
            "username": owner.username,
            "email": owner.email,
            "full_name": owner.full_name
        }
        
        # Get members with user details
        members, _ = circle_repository.get_circle_members(db, circle_id)
        member_details = []
        for member in members:
            user = user_repository.get_user_by_id(db, member.user_id)
            if user:
                member_details.append({
                    "id": member.id,
                    "circle_id": member.circle_id,
                    "user_id": member.user_id,
                    "role": member.role,
                    "status": member.status,
                    "joined_at": member.joined_at,
                    "invited_by": member.invited_by,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name
                    }
                })
        
        # Combine all data
        result = {
            **circle_data,
            "owner": owner_data,
            "members": member_details
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving circle details {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve circle details"
        )

def update_circle_service(db: Session, circle_id: int, update_data: CircleUpdate, current_user_id: int) -> Dict[str, Any]:
    """Update a circle if the user is the owner or admin."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Check permission
        if not circle_repository.check_user_is_owner_or_admin(db, circle_id, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner or admin can update this circle"
            )
            
        # Update the circle
        updated_circle = circle_repository.update_circle(db, circle, update_data)
        circle_data = circle_repository.get_circle_with_member_count(db, updated_circle.id)
        
        return circle_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update circle"
        )

def delete_circle_service(db: Session, circle_id: int, current_user_id: int) -> None:
    """Delete a circle if the user is the owner."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Check if user is the owner
        if circle.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the circle owner can delete the circle"
            )
            
        # Delete the circle
        circle_repository.delete_circle(db, circle)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete circle"
        )

def get_user_circles_service(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> CircleListResponse:
    """Get all circles where the user is a member or owner."""
    try:
        circles, total = circle_repository.get_user_circles(db, user_id, skip, limit)
        
        # Get member count for each circle
        circle_responses = []
        for circle in circles:
            circle_data = circle_repository.get_circle_with_member_count(db, circle.id)
            circle_responses.append(circle_data)
            
        return CircleListResponse(
            circles=circle_responses,
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error retrieving user circles for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user circles"
        )

# ---- Circle Member Services ----
def add_member_service(db: Session, circle_id: int, member_data: CircleMemberCreate, current_user_id: int) -> CircleMemberResponse:
    """Add a member to a circle if the user is authorized."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Check if user is owner or admin
        if not circle_repository.check_user_is_owner_or_admin(db, circle_id, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner or admin can add members"
            )
            
        # Check if user exists
        user = user_repository.get_user_by_id(db, member_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Add the member
        member = circle_repository.add_member(db, circle_id, member_data, current_user_id)
        return member
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding member to circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add member to circle"
        )

def invite_member_service(db: Session, circle_id: int, invite_data: CircleMemberInvite, current_user_id: int) -> CircleMemberResponse:
    """Invite a member to a circle if the user is authorized."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Check if user is owner or admin
        if not circle_repository.check_user_is_owner_or_admin(db, circle_id, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner or admin can invite members"
            )
            
        # Check if user exists
        user = user_repository.get_user_by_id(db, invite_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Check if user is already in circle
        existing_member = circle_repository.get_circle_member(db, circle_id, invite_data.user_id)
        if existing_member and existing_member.status == "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this circle"
            )
            
        # Invite the member
        member = circle_repository.invite_member(db, circle_id, invite_data, current_user_id)
        return member
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inviting member to circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to invite member to circle"
        )

def update_member_service(db: Session, circle_id: int, member_user_id: int, update_data: CircleMemberUpdate, current_user_id: int) -> CircleMemberResponse:
    """Update a member's role or status if authorized."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Get the member
        member = circle_repository.get_circle_member(db, circle_id, member_user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
            
        # Check permissions
        if not circle_repository.check_user_is_owner_or_admin(db, circle_id, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner or admin can update members"
            )
            
        # Prevent changing owner role
        if member.role == "owner" and update_data.role and update_data.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The owner's role cannot be changed"
            )
            
        # Update the member
        updated_member = circle_repository.update_member(db, member, update_data)
        return updated_member
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating member in circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update circle member"
        )

def remove_member_service(db: Session, circle_id: int, member_user_id: int, current_user_id: int) -> None:
    """Remove a member from a circle if authorized."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Get the member
        member = circle_repository.get_circle_member(db, circle_id, member_user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
            
        # Check permissions
        is_owner_or_admin = circle_repository.check_user_is_owner_or_admin(db, circle_id, current_user_id)
        is_self_removal = member_user_id == current_user_id
        
        if not (is_owner_or_admin or is_self_removal):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner, admin, or the member themselves can remove membership"
            )
            
        # Prevent removing the owner
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The owner cannot be removed from the circle"
            )
            
        # Remove the member
        circle_repository.remove_member(db, member)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing member from circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove circle member"
        )

def get_circle_members_service(db: Session, circle_id: int, current_user_id: int, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
    """Get all members of a circle with pagination."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Check access permission
        if circle.is_private and not _check_circle_access(db, circle, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this circle"
            )
            
        # Get the members
        members, total = circle_repository.get_circle_members(db, circle_id, skip, limit)
        
        # Get user details for each member
        member_details = []
        for member in members:
            user = user_repository.get_user_by_id(db, member.user_id)
            if user:
                member_details.append({
                    "id": member.id,
                    "circle_id": member.circle_id,
                    "user_id": member.user_id,
                    "role": member.role,
                    "status": member.status,
                    "joined_at": member.joined_at,
                    "invited_by": member.invited_by,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name
                    }
                })
                
        return {
            "members": member_details,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving members for circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve circle members"
        )

# ---- Notes in Circle Service ----
def get_circle_notes_service(db: Session, circle_id: int, current_user_id: int, skip: int = 0, limit: int = 100):
    """Get all notes shared with a circle."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Circle not found"
            )
            
        # Check membership/ownership
        member_ids = [m.user_id for m in circle.members]
        if current_user_id != circle.owner_id and current_user_id not in member_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
            
        notes, total = circle_repository.get_circle_notes(db, circle_id, skip, limit)
        
        return {
            "notes": notes,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving notes for circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve circle notes"
        )

def add_note_to_circle_service(db: Session, circle_id: int, note_id: int, current_user_id: int):
    """Add a note to a circle if the user is authorized."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Get the note
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
            
        # Check if user is the note owner
        if note.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only share your own notes"
            )
            
        # Check if user is a member of the circle
        if not circle_repository.check_user_is_member(db, circle_id, current_user_id) and circle.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of the circle to share notes with it"
            )
            
        # Add note to circle
        circle_repository.add_note_to_circle(db, circle_id, note_id)
        
        # Return the full note object rather than just the join record
        return note
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding note {note_id} to circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add note to circle"
        )

def remove_note_from_circle_service(db: Session, circle_id: int, note_id: int, current_user_id: int):
    """Remove a note from a circle if the user is authorized."""
    try:
        # Get the circle
        circle = circle_repository.get_circle(db, circle_id)
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found"
            )
            
        # Get the note
        note = db.query(Note).filter(Note.id == note_id).first()
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found"
            )
            
        # Check if user is the note owner or circle owner/admin
        is_note_owner = note.user_id == current_user_id
        is_circle_authority = circle_repository.check_user_is_owner_or_admin(db, circle_id, current_user_id)
        
        if not (is_note_owner or is_circle_authority):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the note owner or circle admin/owner can remove shared notes"
            )
            
        # Remove note from circle
        success = circle_repository.remove_note_from_circle(db, circle_id, note_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note is not shared with this circle"
            )
            
        return {"detail": "Note removed from circle successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing note {note_id} from circle {circle_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove note from circle"
        )

# ---- Helper Functions ----
def _check_circle_access(db: Session, circle, user_id: int) -> bool:
    """Check if a user has access to a circle."""
    if circle.owner_id == user_id:
        return True
        
    return circle_repository.check_user_is_member(db, circle.id, user_id)
