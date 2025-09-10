"""Seed script for development data.

This script populates the database with initial development data.
Run with: python -m scripts.seed_dev
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base
from app.models.user_model import User
from app.services.auth import get_password_hash


def seed_db():
    """Seed the database with initial data."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            print("Creating admin user...")
            # Create admin user
            admin = User(
                email="admin@example.com",
                username="admin",
                full_name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True
            )
            db.add(admin)
        
        # Check if test user exists
        test_user = db.query(User).filter(User.username == "test").first()
        if not test_user:
            print("Creating test user...")
            # Create test user
            test_user = User(
                email="test@example.com",
                username="test",
                full_name="Test User",
                hashed_password=get_password_hash("test123"),
                is_superuser=False
            )
            db.add(test_user)
        
        # Commit changes
        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
