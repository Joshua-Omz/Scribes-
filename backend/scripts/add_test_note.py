"""
Script to add a test note to the database
"""
import os
import sys
from pathlib import Path

# Add project root directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.models.notes_models import Note

def add_test_note():
    """Add a test note to the database"""
    db = SessionLocal()
    try:
        # Check if we have at least one user
        from app.models.user_model import User
        user = db.query(User).first()
        
        if not user:
            print("⚠️ No users found. Please run the seed script first.")
            return
        
        # Create a test note
        note = Note(
            user_id=user.id,
            title="Test Note",
            content="This is a test note created to verify the database connection.",
            preacher="Test Preacher",
            tags="test,verification",
            scripture_refs="John 3:16"
        )
        
        db.add(note)
        db.commit()
        
        print(f"✅ Test note created successfully for user {user.username} (ID: {user.id})")
        return note.id
    except Exception as e:
        print(f"❌ Error creating test note: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_test_note()
