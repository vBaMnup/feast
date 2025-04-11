from unittest.mock import patch, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.database import get_db
from src.reservation import router as reservation_router
from src.tables import router as tables_router
from src.tables.models import Table

app = FastAPI()
app.include_router(reservation_router.router)
app.include_router(tables_router.router)


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


@pytest.fixture(scope="module")
def mock_db_session():
    """Mock database session for testing."""
    db_session = MagicMock()
    return db_session


@pytest.fixture(scope="module", autouse=True)
def override_get_db(mock_db_session):
    """Override get_db function to return mock database session."""
    app.dependency_overrides[get_db] = lambda: mock_db_session
    yield
    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def client():
    """Create a test client for testing."""
    with TestClient(app) as c:
        yield c
