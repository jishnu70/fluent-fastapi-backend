from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.future import select
from models.User import User
from schemas import UserSchema
from core import encryption
import logging
from database import get_db
from typing import Annotated

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def create_new_user(db:Annotated[AsyncSession, Depends(get_db)], user_data:UserSchema.UserCreate):
    try:
        hash_password = encryption.hash_password(user_data.password)
        user = User(
            user_name = user_data.username,
            email = user_data.email,
            public_key = user_data.public_key,
            password = hash_password,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user.id
    except Exception as e:
        await db.rollback()
        logger.error(e)

async def get_user_by_username(db:Annotated[AsyncSession, Depends(get_db)], username:str):
    try:
        user = await db.execute(select(User).filter_by(user_name=username))
        return user.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Error fetching user by username: {e}")
        return None

async def get_current_user(db:Annotated[AsyncSession, Depends(get_db)], token:Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = encryption.decode_jwt_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        logger.error(f"Error fetching user by username: {JWTError}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Error fetching user by username: {e}")
        raise credentials_exception
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user
