# routes/admin.py
import os
import logging
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.context import CryptContext
from dotenv import load_dotenv

from models import User, WineCellar, WineBottle, Permission
from dependencies import API_PATH_ROOT, get_db
# import schemas

# prefix="/admin",
router = APIRouter(prefix=API_PATH_ROOT, tags=["admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv()

@router.get("/clean", status_code=status.HTTP_201_CREATED)
def clean_database(db: Session = Depends(get_db)):
    try:
        db.query(WineBottle).delete()
        db.query(WineCellar).delete()
        db.query(Permission).delete()
        db.query(User).delete()
        db.commit()
    except Exception as e:
        logging.exception("Unexpected error while cleaning database: %s", e)
        db.rollback()
        raise
    return {"detail": "Database cleaned"}

@router.get("/init", status_code=status.HTTP_201_CREATED)
def init_database(db: Session = Depends(get_db)):
    # Récupérer les informations d'admin depuis les variables d'environnement
    name = os.getenv("ADMIN_NAME", "admin@example.com")
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin")

    try:
        # Vérifier si un admin existe déjà
        existing_admin = db.query(User).filter(User.is_admin).first() # == True
        if existing_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Admin already exists")

        # Hasher le mot de passe et créer l'utilisateur admin
        hashed_password = pwd_context.hash(password[:72])
        user = User(email=name, username=username, hashed_password=hashed_password, is_admin=True)

        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        logging.warning("Integrity error while creating admin: %s", exc)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Admin already exists or data integrity issue") from exc
    except SQLAlchemyError as exc:
        logging.warning("Database error while creating admin: %s", exc)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Database error") from exc
    except Exception as exc:
        logging.exception("Unexpected error while creating admin: %s", exc)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Unexpected error") from exc

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
