# Scribes Backend Implementation Report

**Date:** August 31, 2025  
**Status:** Phase 2 - Database Setup

## Table of Contents

1. [Overview](#overview)
2. [Project Structure](#project-structure)
3. [Configuration System](#configuration-system)
4. [Database Setup](#database-setup)
5. [Authentication System](#authentication-system)
6. [API Endpoints](#api-endpoints)
7. [Middleware](#middleware)
8. [Development Environment](#development-environment)
9. [Current Progress](#current-progress)
10. [Next Steps](#next-steps)

## Overview

The Scribes backend is a FastAPI-based REST API designed to support a note-taking application with advanced features like scripture tagging, cross-references, and reminders. The architecture follows modern best practices with a clear separation of concerns, making it maintainable and scalable.

## Project Structure

The backend follows a well-organized modular structure:

```
backend/
├── app/                      # Main application package
│   ├── db/                   # Database configuration and repositories
│   │   ├── repositories/     # Repository pattern implementations
│   │   └── database.py       # SQLAlchemy setup
│   ├── middleware/           # Custom middleware components
│   ├── models/               # SQLAlchemy ORM models
│   ├── routes/               # API route handlers
│   ├── schemas/              # Pydantic validation schemas
│   ├── security/             # Authentication and security utilities
│   ├── services/             # Business logic services
│   ├── tests/                # Test modules
│   ├── utils/                # Utility functions
│   ├── workers/              # Background task workers (Celery)
│   ├── config.py             # Application configuration
│   └── main.py               # FastAPI application initialization
├── alembic/                  # Database migration files
├── docs/                     # Documentation files
├── scripts/                  # Utility scripts
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
└── requirements.txt          # Python dependencies
```

This structure implements a clean architecture approach with:
- **Models**: Define database structure
- **Repositories**: Handle database operations
- **Services**: Implement business logic
- **Routes**: Define API endpoints
- **Schemas**: Validate request/response data

## Configuration System

Configuration is handled through a centralized `config.py` module using Pydantic's `BaseSettings` class, which loads values from environment variables with sensible defaults:

```python
class Settings(BaseSettings):
    # Core settings
    APP_NAME: str = "Scribes"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-change-me-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "insecure-jwt-key-change-me")
    JWT_REFRESH_SECRET_KEY: str = os.getenv("JWT_REFRESH_SECRET_KEY", "insecure-jwt-refresh-key-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Database
    DATABASE_URL: PostgresDsn = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/scribes_db")
    
    # CORS
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "*").split(",")
```

An `.env` file contains environment-specific configuration, which is loaded automatically by Pydantic, making it easy to switch between development, testing, and production environments.

## Database Setup

### SQLAlchemy Configuration

Database connection is configured in `app/db/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

# Create SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db() -> Session:
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

This setup follows best practices for FastAPI and SQLAlchemy integration, with the `get_db` dependency function ensuring proper session management.

### Alembic Migrations

Database migrations are managed with Alembic, which is configured to work with the SQLAlchemy models:

```python
# In alembic/env.py
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.db.database import Base
from app.models import user, refresh_token

target_metadata = Base.metadata

def run_migrations_online():
    from app.config import settings
    
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    # ... rest of migration setup
```

The Alembic environment is configured to:
1. Import the SQLAlchemy models
2. Use the metadata from these models for auto-generation
3. Get the database URL from application settings

### Data Models

#### User Model

```python
class User(Base):
    """User database model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### Refresh Token Model

```python
class RefreshToken(Base):
    """RefreshToken database model for storing refresh tokens."""
    
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Repository Pattern

The application implements the repository pattern to abstract database operations, making the code more testable and maintainable:

```python
# Example from user_repository.py
def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_data: UserCreate, hashed_password: str) -> User:
    """Create a new user."""
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

## Authentication System

The authentication system uses JWT (JSON Web Tokens) with refresh tokens for secure, stateless authentication.

### JWT Implementation

JWT handling is implemented in `app/security/jwt.py`:

```python
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire, "token_type": "access"})
    
    # Create JWT token
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
```

This implementation includes:
- Access tokens with shorter lifetime (30 minutes by default)
- Refresh tokens with longer lifetime (7 days by default)
- Separate secret keys for access and refresh tokens
- Token type validation to prevent token misuse
- Proper error handling for expired or invalid tokens

### Password Hashing

Passwords are securely hashed using bcrypt through the passlib library:

```python
# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### Authentication Service

The authentication service (`app/services/auth.py`) handles user authentication, creation, and token generation:

```python
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    # Check if user with email exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # ... similar check for username
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
```

### Refresh Token Storage

Refresh tokens are stored in the database via the `RefreshToken` model, allowing for:
- Token revocation (logout)
- Security auditing
- Prevention of refresh token reuse

## API Endpoints

The API endpoints are organized into routers, with the authentication router (`app/routes/auth.py`) implementing:

```python
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    return create_user(db, user_data)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate a user and issue JWT tokens."""
    # ... authentication logic

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Issue a new access token using a refresh token."""
    # ... token refresh logic

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get information about the current authenticated user."""
    # ... user info retrieval
```

Pydantic schemas ensure proper validation of request and response data:

```python
class UserBase(BaseModel):
    """Base user schema with common attributes."""
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for user creation requests."""
    password: str = Field(..., min_length=8)

class Token(BaseModel):
    """Schema for token responses."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

## Middleware

Custom middleware components handle cross-cutting concerns:

### JWT Authentication Middleware

```python
class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication."""
    
    def __init__(self, app, exclude_paths=None):
        """Initialize the middleware."""
        super().__init__(app)
        self.security = HTTPBearer()
        self.exclude_paths = exclude_paths or []
    
    async def dispatch(self, request: Request, call_next):
        """Process the request."""
        # Check if path is excluded from authentication
        path = request.url.path
        for excluded_path in self.exclude_paths:
            if path.startswith(excluded_path):
                return await call_next(request)
        
        # ... authentication logic
```

This middleware is configured in `main.py` to exclude certain paths from authentication requirements:

```python
app.add_middleware(
    JWTAuthMiddleware,
    exclude_paths=[
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/refresh",
    ],
)
```

## Development Environment

The development environment is configured using Docker Compose:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_USER: scribes_user
      POSTGRES_PASSWORD: scribes_password
      POSTGRES_DB: scribes_db
    # ... other configuration

  redis:
    image: redis:alpine
    # ... configuration

  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+psycopg://scribes_user:scribes_password@db/scribes_db
      # ... other environment variables
    volumes:
      - ./:/app
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  worker:
    build:
      context: .
      dockerfile: Dockerfile
    # ... worker configuration
    command: ["celery", "-A", "app.workers.worker", "worker", "--loglevel=info"]
```

This setup provides:
- PostgreSQL database
- Redis for caching and Celery task queue
- API service with hot-reloading for development
- Celery worker for background tasks

## Current Progress

### Completed
- Project structure setup
- Configuration system
- Database connection with SQLAlchemy
- Alembic integration for migrations
- User and RefreshToken models
- Authentication system with JWT
- Repository pattern implementation
- API endpoints for authentication
- JWT middleware
- Docker and Docker Compose setup

### In Progress
- Database migration for initial schema
- Testing database connection

### Pending
- Additional models for notes, tags, etc.
- API endpoints for note management
- Cross-reference functionality
- Reminder scheduling
- Export capabilities

## Next Steps

1. **Complete Database Migration**: Run the first migration to create the database schema
2. **Test Database Connection**: Verify the application can connect to the database
3. **Create Seed Data**: Add initial data for development
4. **Implement Note Models**: Create models for notes and related entities
5. **Build Note API Endpoints**: Implement CRUD operations for notes
6. **Add Scripture Tagging**: Implement logic for detecting and linking scripture references
7. **Develop Cross-Reference System**: Create algorithms for building cross-references between notes
8. **Implement Reminder System**: Add scheduling and notification for reminders

## Technical Details

### Database Schema

The current schema includes:

**Users Table**
- `id`: Integer (primary key)
- `email`: String (unique, indexed)
- `username`: String (unique, indexed)
- `hashed_password`: String
- `full_name`: String (optional)
- `is_active`: Boolean (default true)
- `is_superuser`: Boolean (default false)
- `created_at`: DateTime (auto-set)
- `updated_at`: DateTime (auto-updated)

**RefreshTokens Table**
- `id`: Integer (primary key)
- `token`: String (unique, indexed)
- `user_id`: Integer (foreign key to users.id)
- `expires_at`: DateTime
- `revoked`: Boolean (default false)
- `created_at`: DateTime (auto-set)
- `updated_at`: DateTime (auto-updated)

### Authentication Flow

1. **Registration**
   - User submits email, username, and password
   - System validates uniqueness of email and username
   - Password is hashed with bcrypt
   - User record is created in database

2. **Login**
   - User submits username and password
   - System validates credentials
   - System generates access and refresh tokens
   - Tokens are returned to the client

3. **Protected Resource Access**
   - Client includes access token in Authorization header
   - JWT middleware validates the token
   - If valid, request proceeds to the handler
   - If invalid, 401 Unauthorized response is returned

4. **Token Refresh**
   - Client submits refresh token
   - System validates the refresh token
   - If valid, new access and refresh tokens are issued
   - Old refresh token can be revoked (not implemented yet)

### Security Considerations

- Passwords are hashed using bcrypt
- JWT tokens have appropriate expiration times
- Access and refresh tokens use different secret keys
- Token type is enforced to prevent token misuse
- CORS is properly configured to restrict origins
- JWT middleware protects routes from unauthorized access

### Testing Approach

The test modules (`app/tests/`) include:

- Unit tests for JWT functionality
- Unit tests for authentication service
- Integration tests for authentication API endpoints

This provides good coverage of the authentication system, ensuring it works as expected.

---

This report provides a comprehensive overview of the current state of the Scribes backend implementation. The project has a solid foundation with a well-structured codebase, robust authentication system, and proper database integration. The next steps focus on implementing the core functionality of the application, including note management, scripture tagging, cross-references, and reminders.
