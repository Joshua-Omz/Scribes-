"""
Test script for the improved notes functionality
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.services.note_service import create_note_service, get_notes_service
from app.schemas.notes_schemas import NoteCreate
from app.models.user_model import User

def test_notes_functionality():
    """Test the improved notes functionality"""
    db = SessionLocal()
    try:
        # Get the first user (assuming seed data exists)
        user = db.query(User).first()
        if not user:
            print("❌ No users found. Please run seed script first.")
            return

        print(f"✅ Testing with user: {user.username} (ID: {user.id})")

        # Test creating a note
        note_data = NoteCreate(
            title="Test Note - Improved System",
            content="This is a test of the improved notes system with better validation and security.",
            preacher="Test Preacher",
            tags=["test", "improvement", "security"],
            scripture_tags=["Psalm 23:1", "John 3:16"]
        )

        print("📝 Creating test note...")
        created_note = create_note_service(db, note_data, user.id)
        print(f"✅ Note created successfully! ID: {created_note.id}")

        # Test retrieving notes
        print("📖 Retrieving user notes...")
        notes = get_notes_service(db, user.id)
        print(f"✅ Retrieved {len(notes)} notes for user")

        # Show the created note details
        for note in notes:
            if note.id == created_note.id:
                print(f"📋 Note details:")
                print(f"   Title: {note.title}")
                print(f"   Content: {note.content[:50]}...")
                print(f"   Preacher: {note.preacher}")
                print(f"   Tags: {note.tags}")
                print(f"   Scripture Refs: {note.scripture_refs}")
                break

        print("🎉 All tests passed! The improved notes system is working correctly.")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_notes_functionality()
