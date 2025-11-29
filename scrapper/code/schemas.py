# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ---- Shared / base ----
class TokenOut(BaseModel):
    id: str
    user_id: int
    token: str
    expires_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True


class ErrorOut(BaseModel):
    error: str
    message: str


# ---- Users ----
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=1, max_length=128)


class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ---- Permissions ----
class PermissionCreate(BaseModel):
    name: str
    description: Optional[str]


class PermissionOut(BaseModel):
    id: str
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


# ---- Wine Cellars ----
class WineCellarCreate(BaseModel):
    name: str
    location: Optional[str]
    capacity: Optional[int]


class WineCellarUpdate(BaseModel):
    name: Optional[str]
    location: Optional[str]
    capacity: Optional[int]


class WineCellarOut(BaseModel):
    id: str
    user_id: int
    name: str
    location: Optional[str]
    capacity: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ---- Wine Bottles ----
class WineBottleCreate(BaseModel):
    name: str
    vintage: Optional[int] = None
    wine_type: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = 1
    image_url: Optional[str] = None
    notes: Optional[str] = None
    scrape: bool = False


class WineBottleUpdate(BaseModel):
    name: Optional[str] = None
    vintage: Optional[int] = None
    wine_type: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    price: Optional[float] = 0.0
    quantity: Optional[int] = 1
    image_url: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class WineBottleOut(BaseModel):
    id: str
    cellar_id: str
    name: str
    vintage: int
    wine_type: str
    region: Optional[str]
    country: Optional[str]
    price: Optional[float]
    quantity: Optional[int]
    image_url: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

