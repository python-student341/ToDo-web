from envparse import Env
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi import Depends

env = Env()

DATABASE_URL = env.str('DATABASE_URL', default='postgresql+asyncpg://postgres:postgres@localhost:5432/todouserdb')

engine = create_async_engine(DATABASE_URL, future=True, echo=False)

new_session = async_sessionmaker(autoflush=False, expire_on_commit=False, bind=engine)

#Some functions
async def get_session():
    async with new_session() as session:
        yield session

session_dep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    pass