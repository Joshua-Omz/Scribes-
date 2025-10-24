# Database Connection Testing Guide

## Overview

This guide documents the process of testing database connectivity for the Scribes backend application. Database connectivity is a crucial first step in ensuring that your application can interact with its data store properly.

## Prerequisites

- Python environment with SQLAlchemy installed
- PostgreSQL database server running
- Database credentials (username, password, host, port, database name)

## Testing Database Connection

### Method 1: Using the Built-in Test Script

The Scribes application includes a test script located at `app/tests/test_db.py` that checks database connectivity by querying the User model:

```python
from app.db.database import SessionLocal
from app.models.user import User

def test_connection():
    db = SessionLocal()
    try:
      users = db.query(User).all()
      print("✅ Database connected, users:", users)
    except Exception as e:
        print("❌ Database connection failed:", e)  
    finally:
        db.close()  

if __name__ == "__main__":
    test_connection()
```

Running this script using the module approach ensures proper path resolution:

```bash
python -m app.tests.test_db
```

### Method 2: Simplified Direct Connection Test

For troubleshooting purposes, we created a simplified test script that bypasses the application's configuration system and directly tests database connectivity:

```python
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Hardcode database URL for testing
DATABASE_URL = "postgresql://postgres:bbjbbjbbj371419@localhost:5432/scribes_db"

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
```

This script can be run directly from the project root:

```bash
python test_db_simple.py
```

## Common Issues and Solutions

### Module Not Found Errors

If you encounter `ModuleNotFoundError: No module named 'app'` when running the test script directly, it means Python cannot locate the application modules. This typically happens because the project root is not in the Python path.

**Solution:** Use one of these approaches:
1. Run as a module: `python -m app.tests.test_db`
2. Add the project root to the Python path in your script:
   ```python
   import os
   import sys
   sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
   ```

### SQLAlchemy Text Expression Error

In newer versions of SQLAlchemy (≥ 2.0), raw SQL strings need to be explicitly marked as text expressions:

**Error:**
```
Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
```

**Solution:**
```python
from sqlalchemy import text
result = db.execute(text("SELECT 1"))  # Use text() function
```

### Database Connection Failures

If the connection fails, check:
1. The database server is running
2. Credentials are correct
3. Network connectivity (especially if using a remote database)
4. Firewall settings
5. PostgreSQL permission settings in `pg_hba.conf`

## Testing in Different Environments

### Local Development

For local testing, ensure your `.env` file contains the correct database connection URL:

```
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### CI/CD Pipelines

For automated testing in CI/CD pipelines, consider using a test database or an in-memory SQLite database to avoid dependencies on external services.

### Production

Always use secure credentials and consider using environment variables or a secure secret management system rather than hardcoding values.

## Conclusion

Regular database connectivity testing helps ensure your application remains functional. Incorporate these tests into your development workflow and CI/CD pipelines for early detection of potential issues.

Remember to keep your database credentials secure and never commit sensitive information to version control.
