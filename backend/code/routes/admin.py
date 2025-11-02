# routes/admin.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from dependencies import get_db
from models import User, WineCellar, WineBottle, Permission
import schemas
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
import logging

# prefix="/admin", 
router = APIRouter(tags=["admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

@router.get("/clean", status_code=status.HTTP_201_CREATED)
def clean_database(db: Session = Depends(get_db)):
    # Vider toutes les tables dans l'ordre pour respecter les FK
    try:
        db.query(WineBottle).delete()
        db.query(WineCellar).delete()
        db.query(Permission).delete()
        db.query(User).delete()
        db.commit()
    except Exception as e:
        logging.warning(e)
    return {"detail": "Database cleaned"}

@router.get("/init", status_code=status.HTTP_201_CREATED)
def init_database(db: Session = Depends(get_db)):
    # Vider toutes les tables dans l'ordre pour respecter les FK
    try:
        name=os.getenv("ADMIN_NAME", "admin@example.com")
        username=os.getenv("ADMIN_USERNAME", "admin")
        password=os.getenv("ADMIN_PASSWORD", "admin")
        hashed = pwd_context.hash(password[:72])
        user = User(email=name, username=username, hashed_password=hashed, is_admin=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        logging.warning(e)
    return {"detail": "Admin created"}

@router.get("/", status_code=status.HTTP_201_CREATED)
def home(db: Session = Depends(get_db)):
    # Vider toutes les tables dans l'ordre pour respecter les FK
    db.query(WineBottle).delete()
    db.query(WineCellar).delete()
    db.query(Permission).delete()
    db.query(User).delete()
    db.commit()
    return {"detail": "Hello World!"}