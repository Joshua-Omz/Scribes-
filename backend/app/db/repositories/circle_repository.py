from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.models.circle_models import Circle, CircleMember, CircleNote
from app.models.notes_models import Note
from app.schemas.circle_schemas import CircleCreate, CircleUpdate, CircleMemberCreate, CircleMemberUpdate, CircleMemberInvite
from typing import List, Optional, Tuple, Dict, Any

# ---- Circle CRUD Operations ----
def create_circle(db: Session, circle_data: CircleCreate, owner_id: int) -> Circle:
    """Create a new circle with the given owner."""
    circle = Circle(
        name=circle_data.name,
        description=circle_data.description,
        is_private=circle_data.is_private,
        owner_id=owner_id
    )
    db.add(circle)
    db.commit()
    db.refresh(circle)
    
    # Add owner as a member with "owner" role
    owner_member = CircleMember(
        circle_id=circle.id,
        user_id=owner_id,
        role="owner",
        status="active"
    )
    db.add(owner_member)
    db.commit()
    
    return circle

def get_circle(db: Session, circle_id: int) -> Optional[Circle]:
    """Get a circle by ID."""
    return db.query(Circle).filter(Circle.id == circle_id).first()

def get_circle_with_member_count(db: Session, circle_id: int) -> Optional[Dict[str, Any]]:
    """Get a circle with the count of active members."""
    circle_with_count = db.query(
        Circle,
        func.count(CircleMember.id).filter(CircleMember.status == "active").label("member_count")
    ).outerjoin(
        CircleMember, CircleMember.circle_id == Circle.id
    ).filter(
        Circle.id == circle_id
    ).group_by(
        Circle.id
    ).first()
    
    if not circle_with_count:
        return None
    
    circle, count = circle_with_count
    result = {
        **{c.name: getattr(circle, c.name) for c in circle.__table__.columns},
        "member_count": count
    }
    return result

def update_circle(db: Session, circle: Circle, update_data: CircleUpdate) -> Circle:
    """Update a circle with new data."""
    # Update only the fields that are provided
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(circle, field, value)
        
    db.commit()
    db.refresh(circle)
    return circle

def delete_circle(db: Session, circle: Circle) -> None:
    """Delete a circle."""
    db.delete(circle)
    db.commit()

def get_user_circles(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Circle], int]:
    """Get all circles where the user is owner or member."""
    # First get total count
    total = db.query(Circle).join(
        CircleMember, CircleMember.circle_id == Circle.id
    ).filter(
        or_(
            Circle.owner_id == user_id,
            CircleMember.user_id == user_id
        )
    ).distinct().count()
    
    # Then get paginated results
    circles = db.query(Circle).join(
        CircleMember, CircleMember.circle_id == Circle.id
    ).filter(
        or_(
            Circle.owner_id == user_id,
            CircleMember.user_id == user_id
        )
    ).distinct().offset(skip).limit(limit).all()
    
    return circles, total

# ---- Circle Members CRUD Operations ----
def add_member(db: Session, circle_id: int, member_data: CircleMemberCreate, invited_by: int = None) -> CircleMember:
    """Add a member to a circle."""
    # Check if member already exists
    existing_member = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == member_data.user_id
    ).first()
    
    if existing_member:
        # Update existing member if found
        for field, value in member_data.dict(exclude={"user_id"}).items():
            setattr(existing_member, field, value)
        db.commit()
        db.refresh(existing_member)
        return existing_member
    
    # Create new member
    member = CircleMember(
        circle_id=circle_id,
        user_id=member_data.user_id,
        role=member_data.role,
        status=member_data.status,
        invited_by=invited_by
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def invite_member(db: Session, circle_id: int, invite_data: CircleMemberInvite, inviter_id: int) -> CircleMember:
    """Invite a new member to a circle."""
    # Check if already a member
    existing_member = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == invite_data.user_id
    ).first()
    
    if existing_member:
        if existing_member.status == "active":
            return existing_member  # Already an active member
        # Update status for inactive or previously invited members
        existing_member.status = "invited"
        existing_member.invited_by = inviter_id
        db.commit()
        db.refresh(existing_member)
        return existing_member
    
    # Create new invitation
    member = CircleMember(
        circle_id=circle_id,
        user_id=invite_data.user_id,
        role=invite_data.role,
        status="invited",
        invited_by=inviter_id
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def update_member(db: Session, member: CircleMember, update_data: CircleMemberUpdate) -> CircleMember:
    """Update a circle member."""
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(member, field, value)
    
    db.commit()
    db.refresh(member)
    return member

def remove_member(db: Session, member: CircleMember) -> None:
    """Remove a member from a circle."""
    db.delete(member)
    db.commit()

def get_circle_member(db: Session, circle_id: int, user_id: int) -> Optional[CircleMember]:
    """Get a specific member of a circle."""
    return db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == user_id
    ).first()

def get_circle_members(db: Session, circle_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[CircleMember], int]:
    """Get all members of a circle with pagination."""
    total = db.query(CircleMember).filter(CircleMember.circle_id == circle_id).count()
    
    members = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id
    ).offset(skip).limit(limit).all()
    
    return members, total

def get_member_count(db: Session, circle_id: int) -> int:
    """Get the count of active members in a circle."""
    return db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.status == "active"
    ).count()

def check_user_is_member(db: Session, circle_id: int, user_id: int) -> bool:
    """Check if a user is an active member of the circle."""
    member = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == user_id,
        CircleMember.status == "active"
    ).first()
    return member is not None

def check_user_is_owner_or_admin(db: Session, circle_id: int, user_id: int) -> bool:
    """Check if a user is the owner or admin of the circle."""
    circle = db.query(Circle).filter(Circle.id == circle_id).first()
    if not circle:
        return False
        
    if circle.owner_id == user_id:
        return True
        
    member = db.query(CircleMember).filter(
        CircleMember.circle_id == circle_id,
        CircleMember.user_id == user_id,
        CircleMember.role.in_(["owner", "admin"]),
        CircleMember.status == "active"
    ).first()
    
    return member is not None

# ---- Circle Notes Operations ----
def add_note_to_circle(db: Session, circle_id: int, note_id: int) -> CircleNote:
    """Add a note to a circle."""
    # Check if note is already in the circle
    existing_note = db.query(CircleNote).filter(
        CircleNote.circle_id == circle_id,
        CircleNote.note_id == note_id
    ).first()
    
    if existing_note:
        return existing_note
        
    circle_note = CircleNote(circle_id=circle_id, note_id=note_id)
    db.add(circle_note)
    db.commit()
    db.refresh(circle_note)
    return circle_note

def remove_note_from_circle(db: Session, circle_id: int, note_id: int) -> bool:
    """Remove a note from a circle."""
    circle_note = db.query(CircleNote).filter(
        CircleNote.circle_id == circle_id,
        CircleNote.note_id == note_id
    ).first()
    
    if not circle_note:
        return False
        
    db.delete(circle_note)
    db.commit()
    return True

def get_circle_notes(db: Session, circle_id: int, skip: int = 0, limit: int = 100) -> Tuple[List[Note], int]:
    """Get all notes shared with a circle with pagination."""
    # Get total count
    total = db.query(CircleNote).filter(CircleNote.circle_id == circle_id).count()
    
    # Get notes with pagination
    circle_notes = db.query(CircleNote).filter(
        CircleNote.circle_id == circle_id
    ).offset(skip).limit(limit).all()
    
    # Extract the actual notes
    notes = [cn.note for cn in circle_notes]
    
    return notes, total

def check_note_in_circle(db: Session, circle_id: int, note_id: int) -> bool:
    """Check if a note is shared with a circle."""
    circle_note = db.query(CircleNote).filter(
        CircleNote.circle_id == circle_id,
        CircleNote.note_id == note_id
    ).first()
    
    return circle_note is not None

def get_note_circles(db: Session, note_id: int) -> List[Circle]:
    """Get all circles a note is shared with."""
    circle_notes = db.query(CircleNote).filter(CircleNote.note_id == note_id).all()
    circles = [cn.circle for cn in circle_notes]
    return circles
