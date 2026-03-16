
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    role: str = "customer"  # allow setting admin for MVP; remove in production


@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    if payload.role not in ("admin", "customer"):
        raise HTTPException(status_code=400, detail="Invalid role")

    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
        created_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    return {"message": "registered"}


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user.email)
    return {"access_token": token, "token_type": "bearer", "role": user.role, "email": user.email}
