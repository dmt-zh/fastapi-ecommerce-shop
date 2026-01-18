from collections.abc import AsyncGenerator
from typing import Annotated, cast

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings

##############################################################################################

def get_settings(request: Request) -> Settings:
    """Зависимость для получения настроек."""

    return cast(Settings, request.app.state.settings)

##############################################################################################

async def get_async_db_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Зависимость для получения асинхронной сессии базы данных."""

    async with request.app.state.database.session_factory() as session:
        yield session

##############################################################################################

SettingsDep = Annotated[Settings, Depends(get_settings)]
AsyncDatabaseDep = Annotated[AsyncSession, Depends(get_async_db_session)]
OAuth2PasswordRequestFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

##############################################################################################
