from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from src.database import get_db


class TestGetDB:
    """Tests for get_db function."""

    def test_normal_execution(self, mock_session_local, mock_session):
        """
        Test for normal execution.

        Args:
            mock_session_local (MagicMock): Mocked session factory.
            mock_session (MagicMock): Mocked session instance.
        """

        db_generator = get_db()
        db = next(db_generator)

        assert db == mock_session

        try:
            next(db_generator)
            assert False, "Генератор должен вернуть только одно значение"
        except StopIteration:
            pass

        mock_session.close.assert_called_once()

    def test_with_exception_during_usage(self, mock_session_local, mock_session):
        """
        Test for usage with exception during usage.

        Args:
            mock_session_local (MagicMock): Mocked session factory.
            mock_session (MagicMock): Mocked session instance.
        """

        db_generator = get_db()
        db = next(db_generator)

        try:
            raise ValueError("Тестовое исключение")
        except ValueError:
            try:
                db_generator.close()
            except:
                pass

        mock_session.close.assert_called_once()

    @patch("src.database.SessionLocal")
    def test_session_creation_error(self, mock_sessionlocal):
        """
        Test for session creation error.

        Args:
            mock_sessionlocal (MagicMock): Mocked session factory.
        """

        mock_sessionlocal.side_effect = OperationalError(
            "mock statement", "mock params", "mock orig"
        )

        with pytest.raises(OperationalError):
            db_generator = get_db()
            next(db_generator)

    def test_context_manager_usage(self, mock_session_local, mock_session):
        """
        Test for context manager usage.

        Args:
            mock_session_local (MagicMock): Mocked session factory.
            mock_session (MagicMock): Mocked session instance.
        """

        db_generator = get_db()
        db = next(db_generator)

        try:
            raise StopIteration()
        except StopIteration:
            try:
                db_generator.close()
            except:
                pass

        mock_session.close.assert_called_once()

    @patch("src.database.SessionLocal")
    def test_multiple_calls(self, mock_sessionlocal, mock_session):
        """
        Test for multiple calls.

        Args:
            mock_sessionlocal (MagicMock): Mocked session factory.
            mock_session (MagicMock): Mocked session instance.
        """

        session1 = MagicMock()
        session2 = MagicMock()
        mock_sessionlocal.side_effect = [session1, session2]

        db_gen1 = get_db()
        db1 = next(db_gen1)

        db_gen2 = get_db()
        db2 = next(db_gen2)

        assert db1 == session1
        assert db2 == session2

        try:
            db_gen1.close()
        except:
            pass

        try:
            db_gen2.close()
        except:
            pass

        session1.close.assert_called_once()
        session2.close.assert_called_once()

    @patch("src.database.SessionLocal")
    def test_db_error_on_close(self, mock_sessionlocal):
        """
        Test for db error on close.

        Args:
            mock_sessionlocal (MagicMock): Mocked session factory.
        """

        session_mock = MagicMock()
        session_mock.close.side_effect = SQLAlchemyError("Ошибка при закрытии")
        mock_sessionlocal.return_value = session_mock

        db_generator = get_db()
        db = next(db_generator)

        with pytest.raises(SQLAlchemyError):
            try:
                db_generator.close()
            except StopIteration:
                pass
