"""
Quick script to verify the database tables that exist
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import inspect, text
from app.db.database import engine

def check_database_tables():
    """Check what tables exist in the database"""
    inspector = inspect(engine)
    
    print("=== Database Tables ===")
    tables = inspector.get_table_names()
    for table in tables:
        print(f"Table: {table}")
        print("  Columns:")
        for column in inspector.get_columns(table):
            print(f"    - {column['name']} ({column['type']})")
        print()
    
    # Check if notes table exists
    if 'notes' in tables:
        print("The 'notes' table exists!")
        
        # Check for any records
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM notes"))
            count = result.scalar()
            print(f"The notes table has {count} records.")
    else:
        print("⚠️ The 'notes' table does NOT exist!")
    
    # Check which migrations have been applied
    if 'alembic_version' in tables:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            print(f"Current database migration version: {version}")

if __name__ == "__main__":
    check_database_tables()
