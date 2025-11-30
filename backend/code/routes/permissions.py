# routes/permissions.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# from database import session_local
import models
import schemas
from dependencies import API_PATH_ROOT

from dependencies import get_db, admin_required

router = APIRouter(prefix=f"{API_PATH_ROOT}/permissions", tags=["Permissions"])


@router.get("", response_model=List[schemas.PermissionOut])
def list_permissions(db: Session = Depends(get_db),
                     current_user: models.User = Depends(admin_required)):
    perms = db.query(models.Permission).all()
    print(current_user)
    return perms


@router.post("", response_model=schemas.PermissionOut, status_code=status.HTTP_201_CREATED)
def create_permission(payload: schemas.PermissionCreate, db: Session = Depends(get_db),
                      current_user: models.User = Depends(admin_required)):
    existing = db.query(models.Permission).filter(models.Permission.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")
    perm = models.Permission(name=payload.name, description=payload.description)
    db.add(perm)
    db.commit()
    db.refresh(perm)
    print(current_user)
    return perm


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(permission_id: str, db: Session = Depends(get_db),
                      current_user: models.User = Depends(admin_required)):
    perm = db.query(models.Permission).filter(models.Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    db.delete(perm)
    db.commit()
    print(current_user)
    # return None
