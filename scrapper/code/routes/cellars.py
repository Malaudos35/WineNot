# routes/cellars.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import session_local
import models
import schemas
from dependencies import *

router = APIRouter(prefix=f"{API_PATH_ROOT}/cellars", tags=["Wine Cellars"])


@router.post("", response_model=schemas.WineCellarOut, status_code=status.HTTP_201_CREATED)
def create_cellar(payload: schemas.WineCellarCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cellar = models.WineCellar(user_id=current_user.id, name=payload.name, location=payload.location, capacity=payload.capacity)
    db.add(cellar)
    db.commit()
    db.refresh(cellar)
    return cellar


@router.get("", response_model=List[schemas.WineCellarOut])
def list_cellars(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cellars = db.query(models.WineCellar).filter(models.WineCellar.user_id == current_user.id).all()
    return cellars


@router.get("/{cellar_id}", response_model=schemas.WineCellarOut)
def get_cellar(cellar_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
    if not cellar:
        raise HTTPException(status_code=404, detail="Cave à vin non trouvée")
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    return cellar


@router.put("/{cellar_id}", response_model=schemas.WineCellarOut)
def update_cellar(cellar_id: str, payload: schemas.WineCellarUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
    if not cellar:
        raise HTTPException(status_code=404, detail="Cave à vin non trouvée")
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    if payload.name is not None:
        cellar.name = payload.name # type: ignore
    if payload.location is not None:
        cellar.location = payload.location # type: ignore
    if payload.capacity is not None:
        cellar.capacity = payload.capacity # type: ignore
    db.add(cellar)
    db.commit()
    db.refresh(cellar)
    return cellar


@router.delete("/{cellar_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cellar(cellar_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
    if not cellar:
        raise HTTPException(status_code=404, detail="Cave à vin non trouvée")
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(cellar)
    db.commit()
    return None
