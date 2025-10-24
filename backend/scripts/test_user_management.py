#!/usr/bin/env python3
"""
User Feature Testing Script

This script tests the user management functionality including:
- User profile operations
- Password changes
- User statistics
- Search and filtering
- Administrative operations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.services.user_service import (
    create_user_service,
    get_user_service,
    get_user_profile_service,
    update_user_service,
    change_password_service,
    search_users_service,
    get_user_stats_service,
    get_recent_users_service,
    deactivate_user_service,
    activate_user_service
)
from app.schemas.user_schemas import UserCreate, UserUpdate, ChangePasswordRequest
from app.services.auth import authenticate_user, create_tokens_for_user
from sqlalchemy.orm import Session
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_user_creation(db: Session):
    """Test user creation with validation."""
    print("\n=== Testing User Creation ===")

    # Test valid user creation
    user_data = UserCreate(
        email="testuser@example.com",
        username="testuser",
        full_name="Test User",
        password="TestPass123"
    )

    try:
        user = create_user_service(db, user_data)
        print(f"✅ User created successfully: {user.username} (ID: {user.id})")
        return user
    except Exception as e:
        print(f"❌ User creation failed: {str(e)}")
        return None


def test_user_profile_operations(db: Session, user):
    """Test user profile operations."""
    print("\n=== Testing User Profile Operations ===")

    # Test get user profile
    try:
        profile = get_user_profile_service(db, user.id)
        print(f"✅ User profile retrieved: {profile.username}")
        print(f"   Notes count: {profile.notes_count}")
        print(f"   Reminders count: {profile.reminders_count}")
    except Exception as e:
        print(f"❌ Profile retrieval failed: {str(e)}")

    # Test update user profile
    update_data = UserUpdate(
        full_name="Updated Test User",
        username="updatedtestuser"
    )

    try:
        updated_user = update_user_service(db, user.id, update_data)
        print(f"✅ User profile updated: {updated_user.full_name}")
    except Exception as e:
        print(f"❌ Profile update failed: {str(e)}")


def test_password_change(db: Session, user):
    """Test password change functionality."""
    print("\n=== Testing Password Change ===")

    # Test password change
    password_data = ChangePasswordRequest(
        current_password="TestPass123",
        new_password="NewTestPass123"
    )

    try:
        change_password_service(db, user.id, password_data)
        print("✅ Password changed successfully")

        # Verify new password works
        auth_user = authenticate_user(db, "updatedtestuser", "NewTestPass123")
        if auth_user:
            print("✅ New password authentication successful")
        else:
            print("❌ New password authentication failed")

    except Exception as e:
        print(f"❌ Password change failed: {str(e)}")


def test_user_statistics(db: Session):
    """Test user statistics functionality."""
    print("\n=== Testing User Statistics ===")

    try:
        stats = get_user_stats_service(db)
        print("✅ User statistics retrieved:")
        print(f"   Total users: {stats.total_users}")
        print(f"   Active users: {stats.active_users}")
        print(f"   Inactive users: {stats.inactive_users}")
        print(f"   Superusers: {stats.superuser_count}")
        print(f"   Recent registrations: {stats.recent_registrations}")
    except Exception as e:
        print(f"❌ Statistics retrieval failed: {str(e)}")


def test_user_search(db: Session):
    """Test user search functionality."""
    print("\n=== Testing User Search ===")

    try:
        # Search for users
        results = search_users_service(db, query="test", skip=0, limit=10)
        print(f"✅ User search successful: {results.total} results found")

        # Test filtering
        active_results = search_users_service(db, is_active=True, skip=0, limit=10)
        print(f"✅ Active user filter: {active_results.total} results")

    except Exception as e:
        print(f"❌ User search failed: {str(e)}")


def test_user_activation(db: Session, user):
    """Test user activation/deactivation."""
    print("\n=== Testing User Activation/Deactivation ===")

    # Test deactivation
    try:
        deactivated_user = deactivate_user_service(db, user.id)
        print(f"✅ User deactivated: {deactivated_user.is_active}")

        # Test activation
        activated_user = activate_user_service(db, user.id)
        print(f"✅ User activated: {activated_user.is_active}")

    except Exception as e:
        print(f"❌ User activation/deactivation failed: {str(e)}")


def test_validation_rules():
    """Test input validation rules."""
    print("\n=== Testing Validation Rules ===")

    from app.schemas.user_schemas import UserCreate

    # Test weak password
    try:
        weak_user = UserCreate(
            email="weak@example.com",
            username="weakuser",
            password="weak"
        )
        print("❌ Weak password validation failed")
    except Exception as e:
        print("✅ Weak password properly rejected")

    # Test invalid username
    try:
        invalid_user = UserCreate(
            email="invalid@example.com",
            username="user@name",  # Invalid character
            password="ValidPass123"
        )
        print("❌ Invalid username validation failed")
    except Exception as e:
        print("✅ Invalid username properly rejected")

    # Test short username
    try:
        short_user = UserCreate(
            email="short@example.com",
            username="ab",  # Too short
            password="ValidPass123"
        )
        print("❌ Short username validation failed")
    except Exception as e:
        print("✅ Short username properly rejected")


def main():
    """Main test function."""
    print("🚀 Starting User Feature Tests...")

    db = next(get_db())

    try:
        # Test validation rules first
        test_validation_rules()

        # Test user creation
        user = test_user_creation(db)
        if not user:
            print("❌ Cannot continue tests without a user")
            return

        # Test user operations
        test_user_profile_operations(db, user)
        test_password_change(db, user)
        test_user_activation(db, user)

        # Test administrative operations
        test_user_statistics(db)
        test_user_search(db)

        print("\n🎉 All User Feature Tests Completed!")

    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


if __name__ == "__main__":
    main()
