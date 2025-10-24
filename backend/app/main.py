"""Main application module.

This module initializes the FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn



from app.config import settings
from app.routes import auth
from app.routes import reminder_routes
from app.routes import notes_routes
from app.routes import user_routes
from app.middleware.jwt_middleware import JWTAuthMiddleware
from app.routes import circle_route as circle_routes

# Create FastAPI app
app = FastAPI(
    title="Scribes API",
    description="API for Scribes note-taking application",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add JWT middleware with excluded paths
app.add_middleware(
    JWTAuthMiddleware,
    exclude_paths=[
        "/",
        "/favicon.ico",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/refresh",
    ],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(reminder_routes.router, prefix="/api")
app.include_router(notes_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(circle_routes.router, prefix="/api" )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": app.version}


if __name__ == "__main__":
    """Run the application using Uvicorn."""
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
