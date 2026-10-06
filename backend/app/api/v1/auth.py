"""Lean JWT login. Uses a plain JSON {email, password} body rather than
OAuth2PasswordRequestForm's form-encoding, to match the frontend's existing
authService.login()/Login.jsx, which already send/collect email+password as
JSON -- not the OAuth2 tutorial's username/form-data convention.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token
from app.db.database import get_db
from app.db.models.user import User
from app.services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=8, max_length=128)


def _issue_token_response(user: User) -> dict:
    token = create_access_token(subject=str(user.id))
    return {
        "token": token,
        "token_type": "bearer",
        "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "userData": {
            "id": str(user.id),
            "email": user.email,
            "role": "admin" if user.is_admin else "user",
        },
    }


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return _issue_token_response(user)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

    user = register_user(db, payload.email, payload.password)
    return _issue_token_response(user)
