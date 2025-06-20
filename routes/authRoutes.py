from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
import logging
from core.encryption import verify_password, create_access_token, create_refresh_token, get_new_access_token_from_refresh_token
from database import get_db
from schemas.UserSchema import UserCreate, UserLogin
from schemas.TokenSchema import TokenResponse, RefreshRequest
from core.authentication import create_new_user, get_current_user, get_user_by_username

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register_user(payload: UserCreate, db:AsyncSession = Depends(get_db)):
    try:
        user = await get_user_by_username(db=db, username=payload.username)
        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        user = await create_new_user(db, payload)
        if not user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        return {"id": user.id, "username": user.user_name, "email": user.email}
    except Exception as e:
        logger.error(f"Error creating a new user: {e}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"message":str(e)})

@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        db_user = await get_user_by_username(db, form_data.username)
        if not db_user or not verify_password(form_data.password, db_user.password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail={"message": "invalid username"})
        access_token = create_access_token({"sub":db_user.user_name})
        refresh_token = create_refresh_token({"sub": db_user.user_name})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer"
        }
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

@router.post("/refresh", response_model=TokenResponse)
async def get_new_access_token(request: RefreshRequest):
    try:
        new_access_token = get_new_access_token_from_refresh_token(request.refresh_token)
        if not new_access_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        return {
            "access_token": new_access_token,
            "refresh_token": request.refresh_token,  # reuse same refresh token or rotate if desired
            "token_type": "Bearer"
        }
    except Exception as e:
        logger.error(f"Refresh failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh failed")
