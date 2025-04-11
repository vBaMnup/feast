from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.tables.models import Table


@pytest.fixture
def mock_session():
    """Fixture for mock session"""

    session_mock = MagicMock()
    return session_mock


@pytest.fixture
def mock_session_local(mock_session):
    """Fixture for mock session local"""

    with patch("src.database.SessionLocal", return_value=mock_session):
        yield


@pytest.fixture
def setup_database():
    """Setup database for tests."""

    engine = create_engine("postgresql://user:password@localhost:5432/test_dbname")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def create_test_table(setup_database):
    """Create a test table for testing."""
    session = setup_database

    test_table = Table(name="Тестовый стол", seats=4, location="Зал 1")
    session.add(test_table)
    session.commit()

    return test_table
