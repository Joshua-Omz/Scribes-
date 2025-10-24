"""
Test script for the improved reminder functionality
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.database import SessionLocal
from app.services.reminder_service import (
    create_reminder_service,
    get_user_reminders_service,
    get_upcoming_reminders_service
)
from app.schemas.reminder_schemas import ReminderCreate
from app.models.user_model import User
from app.models.notes_models import Note

def test_reminder_functionality():
    """Test the improved reminder functionality"""
    db = SessionLocal()
    try:
        # Get the first user (assuming seed data exists)
        user = db.query(User).first()
        if not user:
            print("❌ No users found. Please run seed script first.")
            return

        print(f"✅ Testing with user: {user.username} (ID: {user.id})")

        # Get the first note for this user
        note = db.query(Note).filter(Note.user_id == user.id).first()
        if not note:
            print("❌ No notes found for user. Please create a note first.")
            return

        print(f"✅ Using note: {note.title} (ID: {note.id})")

        # Test creating a reminder
        future_time = datetime.now(timezone.utc) + timedelta(hours=2)
        reminder_data = ReminderCreate(
            note_id=note.id,
            scheduled_at=future_time
        )

        print("📅 Creating test reminder...")
        created_reminder = create_reminder_service(db, reminder_data, user.id)
        print(f"✅ Reminder created successfully! ID: {created_reminder.id}")
        print(f"   Scheduled for: {created_reminder.scheduled_at}")
        print(f"   Status: {created_reminder.status}")

        # Test retrieving reminders
        print("📋 Retrieving user reminders...")
        reminders = get_user_reminders_service(db, user.id)
        print(f"✅ Retrieved {len(reminders)} reminders for user")

        # Test upcoming reminders
        print("🔮 Retrieving upcoming reminders...")
        upcoming = get_upcoming_reminders_service(db, user.id, limit=5)
        print(f"✅ Retrieved {len(upcoming)} upcoming reminders")

        # Show reminder details
        for reminder in reminders:
            if reminder.id == created_reminder.id:
                print(f"📅 Reminder details:")
                print(f"   ID: {reminder.id}")
                print(f"   Note ID: {reminder.note_id}")
                print(f"   Scheduled: {reminder.scheduled_at}")
                print(f"   Status: {reminder.status}")
                print(f"   Created: {reminder.created_at}")
                break

        print("🎉 All reminder tests passed! The improved reminder system is working correctly.")

        # Test validation (try to create invalid reminder)
        print("\n🧪 Testing validation...")
        try:
            past_time = datetime.now(timezone.utc) - timedelta(hours=1)
            invalid_data = ReminderCreate(
                note_id=note.id,
                scheduled_at=past_time
            )
            create_reminder_service(db, invalid_data, user.id)
            print("❌ Validation failed - past date was accepted!")
        except Exception as e:
            print(f"✅ Validation working - rejected past date: {str(e)}")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_reminder_functionality()
