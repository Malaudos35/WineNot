# routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import session_local
import models
import schemas
from dependencies import *
from passlib.context import CryptContext
from typing import List
from dependencies import get_current_user, get_db, admin_required

router = APIRouter(prefix=f"{API_PATH_ROOT}/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter((models.User.email == payload.email) | (models.User.username == payload.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email or username already registered")

    hashed = pwd_context.hash(payload.password[:72])
    user = models.User(email=payload.email, username=payload.username, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=List[schemas.UserOut])
def list_users(db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    users = db.query(models.User).all()
    return users



@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    # allow users to access only themselves unless admin
    if current_user.id != user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, payload: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if current_user.id != user.id and not current_user.is_admin:  # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")

    if payload.email:
        user.email = payload.email # type: ignore
    if payload.username:
        user.username = payload.username # type: ignore
    if payload.password:
        user.hashed_password = pwd_context.hash(payload.password) # type: ignore

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email déjà utilisé")

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(admin_required)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    db.delete(user)
    db.commit()
    return None
