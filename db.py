from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import models


DATABASE_URL = "sqlite+aiosqlite:///./test.db"


# Base = declarative_base()


engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, models.User)
