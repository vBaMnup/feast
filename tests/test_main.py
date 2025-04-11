from unittest.mock import patch, MagicMock

import pytest
from fastapi import status, HTTPException
from fastapi.testclient import TestClient

from src.main import app
from src.database import get_db
from src.config import settings


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
            response = client.get(f"{settings.API_PREFIX}/tables/")

            assert response.status_code == status.HTTP_200_OK
            mock_get_tables.assert_called_once()

    def test_reservations_router_mounted(self, client):
        """Test the availability of the reservations router."""

        with patch("src.reservation.router.get_reservations") as mock_get_reservations:
            mock_get_reservations.return_value = []
            response = client.get(f"{settings.API_PREFIX}/reservations/")
            assert response.status_code == status.HTTP_200_OK
            mock_get_reservations.assert_called_once()

    def test_http_exception_handler(self, client):
        """Test custom exception handler for HTTPException."""
        error_detail = "Simulated HTTP Error 400"

        with patch("src.tables.router.get_tables") as mock_get_tables:
            mock_get_tables.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail
            )
            response = client.get(f"{settings.API_PREFIX}/tables/")
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert response.json() == {"detail": error_detail}

    def test_global_exception_handler(self, client):
        """Test global exception handler for uncaught exceptions."""

        with patch("src.reservation.router.get_reservations") as mock_get_reservations:
            mock_get_reservations.side_effect = Exception("Simulated Internal Error")
            response = client.get(f"{settings.API_PREFIX}/reservations/")
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {
                "detail": "Внутренняя ошибка сервера. Попробуйте позже."
            }

    def test_not_found_exception_root(self, client):
        """Test the exception handler for 404 Not Found."""

        response = client.get("/non/existent/root/path")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not Found"}

    def test_not_found_exception_prefixed(self, client):
        """Test the exception handler for 404 Not Found."""

        response = client.get(f"{settings.API_PREFIX}/non/existent/api/path")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Not Found"}

    def test_openapi_endpoint(self, client):
        """Test the availability of the openapi.json endpoint."""

        response = client.get(f"{settings.API_PREFIX}/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/json"
        assert "openapi" in response.json()
        assert "info" in response.json()
        assert response.json()["info"]["title"] == settings.APP_TITLE

    def test_swagger_docs_endpoint(self, client):
        """Test the availability of the Swagger UI endpoint."""

        response = client.get(f"{settings.API_PREFIX}/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        assert f"{settings.API_PREFIX}/openapi.json" in response.text

    def test_redoc_endpoint(self, client):
        """Test the availability of the ReDoc endpoint."""

        response = client.get(f"{settings.API_PREFIX}/redoc")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]
        expected_url = f"{settings.API_PREFIX}/openapi.json"
        try:
            assert expected_url in response.text
        except AssertionError as e:
            print(f"Expected URL not found. Response text:\n{response.text}")
            raise e
