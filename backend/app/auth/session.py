"""
Session management for authentication.
Handles session creation, validation, and cleanup.
"""
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database.models import Session as SessionModel, User
from app.config import get_settings

settings = get_settings()


def generate_session_id() -> str:
    """
    Generate a secure random session ID.
    
    Returns:
        64-character hexadecimal session ID
    """
    return secrets.token_hex(32)


def create_session(db: Session, user_id: int) -> str:
    """
    Create a new session for a user.
    
    Args:
        db: Database session
        user_id: User ID to create session for
        
    Returns:
        Session ID string
    """
    session_id = generate_session_id()
    expires_at = datetime.utcnow() + timedelta(hours=settings.session_expire_hours)
    
    session = SessionModel(
        session_id=session_id,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    
    return session_id


def validate_session(db: Session, session_id: str) -> tuple[bool, int | None]:
    """
    Validate a session and return the user ID if valid.
    
    Args:
        db: Database session
        session_id: Session ID to validate
        
    Returns:
        Tuple of (is_valid, user_id)
    """
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()
    
    if not session:
        return False, None
    
    # Check if session is expired
    if session.expires_at < datetime.utcnow():
        # Delete expired session
        db.delete(session)
        db.commit()
        return False, None
    
    # Check if user is active
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user or not user.is_active:
        return False, None
    
    return True, session.user_id


def delete_session(db: Session, session_id: str) -> bool:
    """
    Delete a session (logout).
    
    Args:
        db: Database session
        session_id: Session ID to delete
        
    Returns:
        True if session was deleted, False if not found
    """
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id
    ).first()
    
    if session:
        db.delete(session)
        db.commit()
        return True
    
    return False


def cleanup_expired_sessions(db: Session) -> int:
    """
    Delete all expired sessions.
    
    Args:
        db: Database session
        
    Returns:
        Number of sessions deleted
    """
    deleted = db.query(SessionModel).filter(
        SessionModel.expires_at < datetime.utcnow()
    ).delete()
    
    db.commit()
    return deleted
