from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import User
from schemas import UserCreate
from core import encryption

async def create_new_user(db: AsyncSession, user_data:UserCreate.UserCreate):
    hash_password = encryption.hash_password(user_data.password)
    user = User.User(
        user_name = user_data.username,
        email = user_data.email,
        public_key = user_data.public_key,
        password = hash_password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user.id

async def get_user_by_username(db:AsyncSession, username:str):
    try:
        user = await db.execute(select(User).filter_by(user_name=username))
        return user.scalar_one_or_none()
    except Exception as e:
        return None