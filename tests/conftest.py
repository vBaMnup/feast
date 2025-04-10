from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_session():
    """Фикстура для создания мока сессии базы данных."""
    session_mock = MagicMock()
    return session_mock


@pytest.fixture
def mock_session_local(mock_session):
    """Фикстура для создания мока фабрики сессий."""
    with patch('src.database.SessionLocal', return_value=mock_session):
        yield
