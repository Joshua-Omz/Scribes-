"""JWT authentication middleware.

This module provides a middleware for authenticating requests with JWT tokens.
"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

from app.security.jwt import verify_access_token


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT authentication.
    
    This middleware checks for a valid JWT token in the Authorization header
    for protected routes.
    """
    
    def __init__(self, app, exclude_paths=None):
        """Initialize the middleware.
        
        Args:
            app: The FastAPI application
            exclude_paths: List of paths to exclude from authentication
        """
        super().__init__(app)
        self.security = HTTPBearer()
        self.exclude_paths = exclude_paths or []
    
    async def dispatch(self, request: Request, call_next):
        """Process the request.
        
        Args:
            request: The incoming request
            call_next: The next middleware/endpoint
            
        Returns:
            The response from the next middleware/endpoint
        """
        # Check if path is excluded from authentication
        path = request.url.path
        for excluded_path in self.exclude_paths:
            if path.startswith(excluded_path):
                return await call_next(request)
        
        # Check for authentication header
        try:
            auth = request.headers.get("Authorization")
            if not auth:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing Authorization header",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Extract token from header
            scheme, token = auth.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify token
            payload = verify_access_token(token)
            
            # Add user info to request state
            request.state.user = payload
            
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
