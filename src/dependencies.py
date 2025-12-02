from collections.abc import AsyncGenerator, Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.config import Settings
from src.services.database import Base, SessionLocal, async_session_maker, get_settings

##############################################################################################

def get_sync_db_session() -> Generator[Session]:
    """Зависимость для получения сессии базы данных."""

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

##############################################################################################

async def get_async_db_session() -> AsyncGenerator[AsyncSession]:
    """Зависимость для получения асинхронной сессии базы данных."""

    async with async_session_maker() as session:
        yield session

##############################################################################################

SettingsDep = Annotated[Settings, Depends(get_settings)]
SyncDatabaseDep = Annotated[Base, Depends(get_sync_db_session)]
ASyncDatabaseDep = Annotated[Base, Depends(get_async_db_session)]
