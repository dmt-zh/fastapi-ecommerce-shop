from collections.abc import Generator

from sqlalchemy.orm import Session

from src.services.database import SessionLocal


def get_db() -> Generator[Session]:
    """
    Зависимость для получения сессии базы данных.
    Создаёт новую сессию для каждого запроса и закрывает её после обработки.
    """

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
