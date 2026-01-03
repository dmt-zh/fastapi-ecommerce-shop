from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import Settings
from src.services.database.postgresql import Base

##############################################################################################

def get_settings(request: Request) -> Settings:
    """Зависимость для получения настроек."""

    return request.app.state.settings

##############################################################################################

async def get_async_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Зависимость для получения асинхронной сессии базы данных."""

    async with request.app.state.database.session_factory() as session:
        yield session

##############################################################################################

SettingsDep = Annotated[Settings, Depends(get_settings)]
AsyncDatabaseDep = Annotated[Base, Depends(get_async_db_session)]
