"""
Authentication routes for login, logout, and registration.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import bcrypt

from app.database.database import get_db
from app.database.models import User
from app.auth.session import create_session, delete_session
from app.auth.middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=3)


class RegisterRequest(BaseModel):
    """Registration request model."""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class AuthResponse(BaseModel):
    """Authentication response model."""
    session_id: str
    username: str
    message: str


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Bcrypt has a 72-byte limit, so we truncate longer passwords.
    """
    # Truncate to 72 bytes (bcrypt limit) and encode
    password_bytes = password.encode('utf-8')[:72]
    # Hash with random salt
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Return as string for storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Bcrypt has a 72-byte limit, so we truncate longer passwords.
    """
    # Truncate to 72 bytes (bcrypt limit) and encode
    password_bytes = plain_password.encode('utf-8')[:72]
    # Ensure hashed_password is bytes
    hashed_bytes = hashed_password.encode('utf-8')
    
    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except ValueError:
        return False


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Creates a new user account and returns a session ID.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username già esistente. Scegli un altro username."
        )
    
    # Create new user
    hashed_password = hash_password(request.password)
    new_user = User(
        username=request.username,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create session
    session_id = create_session(db, new_user.id)
    
    return AuthResponse(
        session_id=session_id,
        username=new_user.username,
        message="Registrazione completata con successo."
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with username and password.
    
    Returns a session ID that should be included in subsequent requests.
    """
    # Find user
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Username o password non corretti."
        )
    
    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Username o password non corretti."
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Utente disabilitato. Contatta l'amministratore."
        )
    
    # Create session
    session_id = create_session(db, user.id)
    
    return AuthResponse(
        session_id=session_id,
        username=user.username,
        message="Login effettuato con successo."
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    user_id: int = Depends(get_current_user),
    x_session_id: str = ...,
    db: Session = Depends(get_db)
):
    """
    Logout and invalidate the current session.
    """
    # Note: get_current_user already validates the session
    # We need to get the session_id from the header manually or pass it
    # For simplicity, we'll add a header dependency
    from fastapi import Header
    
    # This is a simplified version - in production you'd want to handle this better
    delete_session(db, x_session_id)
    
    return MessageResponse(message="Logout effettuato con successo.")
