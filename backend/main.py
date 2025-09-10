from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn

from app.core.config import settings
from app.core.database import engine, Base
from app.auth.router import router as auth_router
from app.notes.router import router as notes_router
from app.users.router import router as users_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Scribes - Spiritually intelligent note-taking API with AI-assisted paraphrasing, scripture tagging, reminders, and private sharing",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(notes_router, prefix="/api/v1/notes", tags=["Notes"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Scribes API",
        "description": "Spiritually intelligent note-taking with AI assistance",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "scribes-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )