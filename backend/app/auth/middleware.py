"""
Authentication middleware and dependencies for FastAPI.
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.auth.session import validate_session


def get_current_user(
    x_session_id: str = Header(..., alias="X-Session-ID"),
    db: Session = Depends(get_db)
) -> int:
    """
    FastAPI dependency to get current authenticated user.
    
    Validates the session ID from the X-Session-ID header.
    
    Args:
        x_session_id: Session ID from request header
        db: Database session
        
    Returns:
        User ID of authenticated user
        
    Raises:
        HTTPException: If session is invalid or expired
    """
    is_valid, user_id = validate_session(db, x_session_id)
    
    if not is_valid:
        raise HTTPException(
            status_code=401,
            detail="Sessione non valida o scaduta. Effettua nuovamente il login."
        )
    
    return user_id


def get_optional_user(
    x_session_id: str = Header(None, alias="X-Session-ID"),
    db: Session = Depends(get_db)
) -> int | None:
    """
    FastAPI dependency to get current user if authenticated (optional).
    
    Returns None if no session is provided or if session is invalid.
    
    Args:
        x_session_id: Session ID from request header (optional)
        db: Database session
        
    Returns:
        User ID if authenticated, None otherwise
    """
    if not x_session_id:
        return None
    
    is_valid, user_id = validate_session(db, x_session_id)
    return user_id if is_valid else None
