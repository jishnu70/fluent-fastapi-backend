from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session

async def close_db():
    try:
        await engine.dispose()
        print("Database engine disposed")
    except Exception as e:
        print(f"Error closing database: {e}")
        raise
