from logging import Logger

from src.config import Settings
from src.services.database.postgresql import PostgreSQLDatabase


async def make_database(settings: Settings, logger: Logger) -> PostgreSQLDatabase:
    """Инициализация и настройка подключения к базе данных."""
    database = PostgreSQLDatabase(settings=settings, logger=logger)
    await database.startup()
    return database
