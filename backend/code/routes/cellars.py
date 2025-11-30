# routes/cellars.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import models
import schemas
from dependencies import API_PATH_ROOT, get_db, get_current_user
from database import logger

router = APIRouter(prefix=f"{API_PATH_ROOT}/cellars", tags=["Wine Cellars"])


@router.post("", response_model=schemas.WineCellarOut, status_code=status.HTTP_201_CREATED)
def create_cellar(payload: schemas.WineCellarCreate, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
    cellar = models.WineCellar(user_id=current_user.id, name=payload.name,
                               location=payload.location, capacity=payload.capacity)
    db.add(cellar)
    db.commit()
    db.refresh(cellar)
    return cellar


@router.get("", response_model=List[schemas.WineCellarOut])
def list_cellars(db: Session = Depends(get_db),
                 current_user: models.User = Depends(get_current_user)):
    cellars = db.query(models.WineCellar).filter(models.WineCellar.user_id == current_user.id).all()
    return cellars


@router.get("/{cellar_id}", response_model=schemas.WineCellarOut)
def get_cellar(cellar_id: str, db: Session = Depends(get_db),
               current_user: models.User = Depends(get_current_user)):
    try:
        cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
        print("Cellar info")
        if not cellar:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Cave à vin non trouvée")
        if cellar.user_id != current_user.id and not current_user.is_admin:# type: ignore[operator]
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        return cellar
    except SQLAlchemyError as exc:
        logger.error(f"Database error while fetching cellar: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error") from exc


@router.put("/{cellar_id}", response_model=schemas.WineCellarOut)
def update_cellar(cellar_id: str, payload: schemas.WineCellarUpdate,
                  db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
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
def delete_cellar(cellar_id: str, db: Session = Depends(get_db),
                  current_user: models.User = Depends(get_current_user)):
    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
    if not cellar:
        raise HTTPException(status_code=404, detail="Cave à vin non trouvée")
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(cellar)
    db.commit()
    # return None
