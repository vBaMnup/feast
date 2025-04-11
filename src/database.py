from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Get database session

    :return:
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
