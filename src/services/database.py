from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from src.config import Settings


##############################################################################################

class Base(DeclarativeBase):
    pass

##############################################################################################

@lru_cache
def get_settings() -> Settings:
    """Получиние настроек приложения."""

    return Settings()

##############################################################################################

db_uri = 'sqlite:///ecomerce.db'
engine = create_engine(db_uri, echo=True)
SessionLocal = sessionmaker(bind=engine)

##############################################################################################

settings = get_settings()
DATABASE_URL = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@localhost:5432/{settings.postgres_db}'
async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

##############################################################################################
