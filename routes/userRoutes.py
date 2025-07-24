from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Annotated
from database import get_db
from models import User
from core.authentication import get_current_user
from schemas.PublicKeySchema import UpdatePublicKey

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/user", tags=["user"])

@user_router.get("/")
async def get_user_details(user: Annotated[User, Depends(get_current_user)]):
    return user

@user_router.put("/update-public-key", response_model="")
async def update_the_public_key(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    updatePublic: UpdatePublicKey
):
    try:
        user.public_key = updatePublic.public_key
        await db.commit()
        await db.refresh(user)
        return {"status":status.HTTP_200_OK, "message":"updated the public key"}
    except Exception as e:
        await db.rollback()
        logger.error(f"update public key Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid format of data")
