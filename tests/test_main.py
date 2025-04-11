from unittest.mock import patch

import pytest
from fastapi import status, HTTPException
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client for testing."""

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


class TestMainApp:
    """Tests for the main FastAPI app."""

    def test_health_check(self, client):
        """Test the health check endpoint."""

        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

    def test_tables_router_mounted(self, client):
        """Test the availability of the tables router."""

        with patch("src.tables.router.get_tables") as mock_get_tables:
            mock_get_tables.return_value = []
            response = client.get("/tables/")

            assert response.status_code == status.HTTP_200_OK
            mock_get_tables.assert_called_once()

    def test_reservations_router_mounted(self, client):
        """Test the availability of the reservations router."""

        with patch("src.reservation.router.get_reservations") as mock_get_reservations:
            mock_get_reservations.return_value = []
            response = client.get("/reservations/")
            assert response.status_code == status.HTTP_200_OK
            mock_get_reservations.assert_called_once()

    def test_http_exception_handler(self, client):
        """Test custom exception handler for HTTPException."""
        error_detail = "Simulated HTTP Error 400"

        with patch("src.tables.router.get_tables") as mock_get_tables:
            mock_get_tables.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail
            )
            response = client.get("/tables/")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {"detail": error_detail}

    def test_global_exception_handler(self, client):
        """Test global exception handler for uncaught exceptions."""

        with patch("src.reservation.router.get_reservations") as mock_get_reservations:
            mock_get_reservations.side_effect = Exception("Simulated Internal Error")
            response = client.get("/reservations/")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {
                "detail": "Внутренняя ошибка сервера. Попробуйте позже."
            }

    def test_not_found_exception(self, client):
        """Test the exception handler for 404 Not Found."""

        response = client.get("/non/existent/path")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not Found"}
