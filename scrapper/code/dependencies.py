# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
import jwt
import logging

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "change_me_super_secret")
API_PATH_ROOT = os.getenv("API_PATH_ROOT", "")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")


logger = logging

