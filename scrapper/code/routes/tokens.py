# routes/tokens.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
import os
import jwt
from passlib.context import CryptContext
from database import session_local
import models
import schemas
from dependencies import *
from typing import Dict
from pydantic import BaseModel
import uuid

router = APIRouter(prefix=f"{API_PATH_ROOT}/tokens", tags=["Tokens"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "change_me_super_secret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


class TokenRequest(BaseModel):
    email: str
    password: str


@router.post("", response_model=schemas.TokenOut, status_code=status.HTTP_201_CREATED)
def create_token(payload: TokenRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials 1")

    if not pwd_context.verify(payload.password, user.hashed_password):  # type: ignore
        raise HTTPException(status_code=401, detail="Invalid credentials 2")

    now = datetime.utcnow()

    # Supprimer les anciens tokens de ce user
    db.query(models.Token).filter(models.Token.user_id == user.id).delete()

    access_payload = {
        "sub": str(user.id),
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    }
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm="HS256")

    refresh_payload = {
        "sub": str(user.id),
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
        "jti": str(uuid.uuid4()),  # Ajoute un identifiant unique
    }
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm="HS256")

    token_row = models.Token(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(token_row)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Token déjà existant")

    db.refresh(token_row)

    return {
        "id": token_row.id,
        "user_id": user.id,
        "token": access_token,
        "expires_at": token_row.expires_at,
        "created_at": token_row.created_at,
    }


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=schemas.TokenOut)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    # Validate refresh token existence in DB
    token_row = db.query(models.Token).filter(models.Token.refresh_token == payload.refresh_token).first()
    if not token_row:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    try:
        decoded = jwt.decode(payload.refresh_token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        # remove old token row
        db.delete(token_row)
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.query(models.User).filter(models.User.id == token_row.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Create new access token (do not replace refresh token here)
    now = datetime.utcnow()
    access_payload = {
        "sub": str(user.id),
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    }
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm="HS256")

    return {
        "id": token_row.id,
        "user_id": user.id,
        "token": access_token,
        "expires_at": token_row.expires_at,
        "created_at": token_row.created_at,
    }
