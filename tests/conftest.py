from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base


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

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    session = session()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
