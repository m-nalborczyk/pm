from datetime import datetime, timedelta
from typing import Optional
import secrets
from sqlalchemy.orm import Session
from backend.crud import get_user_by_username, verify_password

# Simple in-memory session store for MVP
# In production, use Redis or database
sessions: dict[str, dict] = {}

# Session expiry time
SESSION_EXPIRY_HOURS = 24


def create_session(username: str, user_id: int) -> str:
    """Create a new session and return session token"""
    token = secrets.token_urlsafe(32)
    sessions[token] = {
        "username": username,
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=SESSION_EXPIRY_HOURS)
    }
    return token


def validate_session(token: str) -> Optional[dict]:
    """Validate session token and return user info if valid"""
    if token not in sessions:
        return None
    
    session = sessions[token]
    if datetime.utcnow() > session["expires_at"]:
        # Session expired, remove it
        del sessions[token]
        return None
    
    return {
        "username": session["username"],
        "user_id": session["user_id"]
    }


def delete_session(token: str) -> bool:
    """Delete a session (logout)"""
    if token in sessions:
        del sessions[token]
        return True
    return False


def authenticate(db: Session, username: str, password: str) -> Optional[int]:
    """Validate username and password, return user_id if valid"""
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password_hash):
        return user.id
    return None
