from logging import Logger

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import Settings

##############################################################################################

class Base(DeclarativeBase):
    """Базовый класс для декларативных моделей базы данных."""

##############################################################################################

class PostgreSQLDatabase:
    """Реализация базы данных PostgreSQL."""

    def __init__(self, settings: Settings, logger: Logger | None = None) -> None:
        self._db = settings.postgres_db
        self._user = settings.postgres_user
        self._password = settings.postgres_password
        self._echo_sql = settings.postgres_echo_sql
        self._logger = logger
        self._engine = None
        self.session_factory = None

    ##########################################################################################

    @property
    def database_url(self) -> str:
        """Формирует асинхронный URL для подключения к PostgreSQL."""

        return f'postgresql+asyncpg://{self._user}:{self._password}@localhost:5432/{self._db}'

    ##########################################################################################

    async def startup(self) -> None:
        """Инициализация соединения с базой данных."""

        try:
            db_url = self.database_url.split('@')[1] if '@' in self.database_url else 'localhost'
            self._logger.info(f'Attempting to connect to PostgreSQL at: {db_url}')
            self._engine = create_async_engine(
                self.database_url,
                echo=self._echo_sql,
                pool_pre_ping=True,
            )
            self.session_factory = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
            )

            assert self._engine is not None
            conn = await self._engine.connect()
            await conn.execute(text('SELECT 1'))
            self._logger.info('Database connection test successful')
            await conn.close()

        except ConnectionRefusedError:
            self._logger.exception('Failed to initialize PostgreSQL database')
            raise

    ##########################################################################################

    async def teardown(self) -> None:
        """Закрытие соединения с базой данных."""

        if self._engine:
            await self._engine.dispose()
            self._logger.info('PostgreSQL database connections closed')

##############################################################################################
