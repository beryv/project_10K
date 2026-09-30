import hashlib
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable must be set before starting the app.")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
REVOKED_TOKENS = set()


def hash_password_value(value: str) -> str:
  return hashlib.sha256(value.encode()).hexdigest()


def verify_password(submitted_hash: str, stored_hash: str):
  return submitted_hash == stored_hash


def create_access_token(username: str):
  expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  payload = {"sub": username, "exp": datetime.utcnow() + expires}
  return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def revoke_token(token: str):
  REVOKED_TOKENS.add(token)


def validate_token(token: str, *, allow_revoked: bool = False):
  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate admin credentials",
      headers={"WWW-Authenticate": "Bearer"},
  )
  if not allow_revoked and token in REVOKED_TOKENS:
    raise credentials_exception

  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    if username is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception

  return username


def get_current_admin(token: str = Depends(oauth2_scheme)):
  return validate_token(token)