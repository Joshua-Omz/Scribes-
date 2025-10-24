import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Get database URL from environment variable for security
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/scribes_db"  # Default for local development only
)

def test_connection():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        # Just test the connection
        from sqlalchemy import text
        result = db.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        print("Testing query result:", result.scalar())
    except Exception as e:
        print("❌ Database connection failed:", e)  
    finally:
        db.close()  

if __name__ == "__main__":
    test_connection()
