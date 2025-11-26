from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

db_uri = 'sqlite:///ecomerce.db'

engine = create_engine(db_uri, echo=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
