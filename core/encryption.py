from passlib.context import CryptContext
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from enum import Enum
from fastapi import HTTPException, status

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

class ExpireDates(Enum):
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 7

# to hash password
def hash_password(password:str):
    return pwd_context.hash(password)

# to verify the password
def verify_password(plain:str, hashed:str):
    return pwd_context.verify(plain, hashed)

# generate access token
def create_access_token(data:dict, expires_minutes:int=ExpireDates.ACCESS_TOKEN_EXPIRE_MINUTES.value):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "type": "access"})

    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

# generate refresh token
def create_refresh_token(data:dict, expires_day:int=ExpireDates.REFRESH_TOKEN_EXPIRE_DAYS.value):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=expires_day)
    to_encode.update({"exp": expire, "type": "refresh"})

    return jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

# decode refresh token
def decode_jwt_token(token:str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid Refresh Token")
        return None

# create a new access token based on the refresh token
def get_new_access_token_from_refresh_token(token: str):
    payload = decode_jwt_token(token)
    if payload and payload.get("type") == "refresh":
        user_data = {
            "sub": payload.get("sub"),
            "user_id": payload.get("user_id")
        }
        return create_access_token(data=user_data)

    return None
