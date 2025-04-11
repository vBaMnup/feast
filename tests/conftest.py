from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.tables.models import Table


@pytest.fixture
def mock_session():
    """
    Fixtura for mock session
    :return:
    """

    session_mock = MagicMock()
    return session_mock


@pytest.fixture
def mock_session_local(mock_session):
    """
    Fixtura for mock session
    :param mock_session:
    :return:
    """

    with patch("src.database.SessionLocal", return_value=mock_session):
        yield


@pytest.fixture
def setup_database():
    """
    Fixtura for setup database
    :return:
    """

    engine = create_engine("postgresql://user:password@localhost:5432/test_dbname")
    Base.metadata.create_all(bind=engine)  # Создаем таблицы
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    yield session  # Предоставляем сессию для теста

    session.close()
    Base.metadata.drop_all(bind=engine)  # Очищаем после теста


@pytest.fixture
def create_test_table(setup_database):
    """Создание тестового стола для использования в тестах."""
    session = setup_database

    test_table = Table(name="Тестовый стол", seats=4, location="Зал 1")
    session.add(test_table)
    session.commit()

    return test_table
