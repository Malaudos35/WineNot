# models.py
from datetime import datetime
import uuid
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, Table
)
from sqlalchemy.orm import relationship

from database import Base # type: ignore

# Association table: users <-> permissions (many-to-many)
user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id",
           Integer,
           ForeignKey("users.id", ondelete="CASCADE"),
           primary_key=True
           ),
    Column("permission_id", String(36),
           ForeignKey("permissions.id", ondelete="CASCADE"),
           primary_key=True
           )
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False) # CHANGER
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    permissions = relationship("Permission", secondary=user_permissions, back_populates="users")
    cellars = relationship("WineCellar", back_populates="owner", cascade="all, delete-orphan")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    users = relationship("User", secondary=user_permissions, back_populates="permissions")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    refresh_token = Column(String(512), nullable=False, unique=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User")


class WineCellar(Base):
    __tablename__ = "wine_cellars"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    capacity = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    owner = relationship("User", back_populates="cellars")
    bottles = relationship("WineBottle", back_populates="cellar", cascade="all, delete-orphan")


class WineBottle(Base):
    __tablename__ = "wine_bottles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cellar_id = Column(String(36), ForeignKey("wine_cellars.id", ondelete="CASCADE"),nullable=False)
    name = Column(String(255), nullable=False)
    vintage = Column(Integer, nullable=False)
    wine_type = Column(String(64), nullable=False)
    region = Column(String(255), nullable=True)
    country = Column(String(128), nullable=True)
    price = Column(Float, nullable=True)
    quantity = Column(Integer, default=1)
    image_url = Column(String(1024), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    cellar = relationship("WineCellar", back_populates="bottles")
