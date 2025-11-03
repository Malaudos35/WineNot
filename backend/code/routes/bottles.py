# routes/bottles.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
import models
import schemas
from dependencies import *

router = APIRouter(prefix=API_PATH_ROOT , tags=["Wine Bottles"])


@router.post("/cellars/{cellar_id}/bottles", response_model=schemas.WineBottleOut, status_code=status.HTTP_201_CREATED)
def add_bottle(cellar_id: str, payload: schemas.WineBottleCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
    if not cellar:
        raise HTTPException(status_code=404, detail="Cave à vin non trouvée")
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    bottle = models.WineBottle(
        cellar_id=cellar_id,
        name=payload.name,
        vintage=payload.vintage,
        wine_type=payload.wine_type,
        region=payload.region,
        country=payload.country,
        price=payload.price,
        quantity=payload.quantity or 1,
        image_url=payload.image_url,
        notes=payload.notes
    )
    db.add(bottle)
    db.commit()
    db.refresh(bottle)
    return bottle


@router.get("/cellars/{cellar_id}/bottles", response_model=List[schemas.WineBottleOut])
def list_bottles(cellar_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == cellar_id).first()
    if not cellar:
        raise HTTPException(status_code=404, detail="Cave à vin non trouvée")
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    bottles = db.query(models.WineBottle).filter(models.WineBottle.cellar_id == cellar_id).all()
    return bottles


@router.get("/bottles/{bottle_id}", response_model=schemas.WineBottleOut)
def get_bottle(bottle_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bottle = db.query(models.WineBottle).filter(models.WineBottle.id == bottle_id).first()
    if not bottle:
        raise HTTPException(status_code=404, detail="Bouteille non trouvée")
    cellar = bottle.cellar
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    return bottle


@router.put("/bottles/{bottle_id}", response_model=schemas.WineBottleOut)
def update_bottle(
    bottle_id: str,
    payload: schemas.WineBottleUpdate,  # tous les champs optionnels
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    bottle = db.query(models.WineBottle).filter(models.WineBottle.id == bottle_id).first()
    if not bottle:
        raise HTTPException(status_code=404, detail="Bouteille non trouvée")

    cellar = db.query(models.WineCellar).filter(models.WineCellar.id == bottle.cellar_id).first()
    if not cellar or (cellar.user_id != current_user.id and not current_user.is_admin): # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")

    # Mets à jour uniquement les champs fournis
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bottle, field, value)

    db.commit()
    db.refresh(bottle)
    return bottle


@router.delete("/bottles/{bottle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bottle(bottle_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bottle = db.query(models.WineBottle).filter(models.WineBottle.id == bottle_id).first()
    if not bottle:
        raise HTTPException(status_code=404, detail="Bouteille non trouvée")
    cellar = bottle.cellar
    if cellar.user_id != current_user.id and not current_user.is_admin: # type: ignore
        raise HTTPException(status_code=403, detail="Forbidden")
    db.delete(bottle)
    db.commit()
    return None
