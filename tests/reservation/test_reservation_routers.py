from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi import status

from src.reservation import schemas

MOCK_RESERVATION_DATA = {
    "id": 1,
    "customer_name": "Тестовый Клиент",
    "table_id": 1,
    "reservation_time": datetime(2025, 7, 15, 19, 0, tzinfo=timezone.utc),
    "duration_minutes": 120,
}

MOCK_RESERVATION_OBJ = schemas.Reservation(**MOCK_RESERVATION_DATA)

MOCK_RESERVATION_CREATE_DATA = {
    "customer_name": "Новый Клиент",
    "table_id": 2,
    "reservation_time": "2025-08-20T20:00:00Z",  # Используем строку для POST запроса
    "duration_minutes": 90,
}


class TestReadReservations:
    """Test case GET /reservations/"""

    def test_read_reservations_default(self, client):
        """Test case GET /reservations/ with default parameters."""

        with patch("src.reservation.router.get_reservations") as mock_get:
            mock_get.return_value = [MOCK_RESERVATION_OBJ]
            response = client.get("/reservations/")

            assert response.status_code == status.HTTP_200_OK
            expected_json = [
                {
                    **MOCK_RESERVATION_DATA,
                    "reservation_time": MOCK_RESERVATION_DATA["reservation_time"]
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            ]
            assert response.json() == expected_json
            mock_get.assert_called_once()

            assert mock_get.call_args[0][1] == 0  # skip
            assert mock_get.call_args[0][2] == 100  # limit

    @pytest.mark.parametrize("skip, limit", [(5, 10), (0, 50), (10, 0)])
    def test_read_reservations_pagination(self, client, skip, limit):
        """Test case GET /reservations/ with pagination."""

        with patch("src.reservation.router.get_reservations") as mock_get:
            mock_get.return_value = []
            response = client.get(f"/reservations/?skip={skip}&limit={limit}")

            assert response.status_code == status.HTTP_200_OK
            mock_get.assert_called_once()

            assert mock_get.call_args[0][1] == skip
            assert mock_get.call_args[0][2] == limit

    def test_read_reservations_empty(self, client):
        """Test case GET /reservations/ with empty result."""

        with patch("src.reservation.router.get_reservations") as mock_get:
            mock_get.return_value = []
            response = client.get("/reservations/")

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []
            mock_get.assert_called_once()

    def test_read_reservations_service_error(self, client):
        """Test case GET /reservations/ with service error."""

        with patch("src.reservation.router.get_reservations") as mock_get:
            mock_get.side_effect = Exception("Database error")
            with pytest.raises(Exception) as exc_info:
                client.get("/reservations/")
            assert "Database error" in str(exc_info.value)


class TestCreateReservation:
    """Test case POST /reservations/"""

    def test_create_reservation_success(self, client):
        """Test case POST /reservations/ with success result."""

        created_reservation_obj = schemas.Reservation(
            id=2,
            **schemas.ReservationCreate(**MOCK_RESERVATION_CREATE_DATA).model_dump(),
        )
        with patch("src.reservation.router.create_reservation") as mock_create:
            mock_create.return_value = created_reservation_obj
            response = client.post("/reservations/", json=MOCK_RESERVATION_CREATE_DATA)

            assert response.status_code == status.HTTP_201_CREATED
            expected_json = {
                "id": 2,
                **MOCK_RESERVATION_CREATE_DATA,
                "reservation_time": MOCK_RESERVATION_CREATE_DATA["reservation_time"],
            }
            assert response.json() == expected_json
            mock_create.assert_called_once()

            call_args = mock_create.call_args[0]
            assert isinstance(call_args[1], schemas.ReservationCreate)
            assert (
                call_args[1].customer_name
                == MOCK_RESERVATION_CREATE_DATA["customer_name"]
            )

    def test_create_reservation_conflict(self, client):
        """Test case POST /reservations/ with conflict result."""

        from fastapi import HTTPException

        conflict_exception = HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Конфликт бронирования"
        )
        with patch("src.reservation.router.create_reservation") as mock_create:
            mock_create.side_effect = conflict_exception
            response = client.post("/reservations/", json=MOCK_RESERVATION_CREATE_DATA)

            assert response.status_code == status.HTTP_409_CONFLICT
            assert "Конфликт бронирования" in response.json()["detail"]
            mock_create.assert_called_once()

    def test_create_reservation_validation_error(self, client):
        """Test case POST /reservations/ with validation error."""

        invalid_data = MOCK_RESERVATION_CREATE_DATA.copy()
        invalid_data["duration_minutes"] = -60
        response = client.post("/reservations/", json=invalid_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.json()

    def test_create_reservation_service_error(self, client):
        """Test case POST /reservations/ with service error."""

        with patch("src.reservation.router.create_reservation") as mock_create:
            mock_create.side_effect = Exception("Service error")
            with pytest.raises(Exception) as exc_info:
                client.post("/reservations/", json=MOCK_RESERVATION_CREATE_DATA)
            assert "Service error" in str(exc_info.value)


class TestDeleteReservation:
    """Test case DELETE /reservations/{reservation_id}"""

    def test_delete_reservation_success(self, client, mock_db_session):
        """Test case DELETE /reservations/{reservation_id} with success result."""

        with patch("src.reservation.router.delete_reservation") as mock_delete:
            mock_delete.return_value = MOCK_RESERVATION_OBJ
            reservation_id = MOCK_RESERVATION_OBJ.id
            response = client.delete(f"/reservations/{reservation_id}")

            assert response.status_code == status.HTTP_200_OK
            expected_json = {
                **MOCK_RESERVATION_DATA,
                "reservation_time": MOCK_RESERVATION_DATA["reservation_time"]
                .isoformat()
                .replace("+00:00", "Z"),
            }
            assert response.json() == expected_json
            mock_delete.assert_called_once_with(mock_db_session, reservation_id)

    def test_delete_reservation_not_found_router_logic(self, client, mock_db_session):
        """Test case DELETE /reservations/{reservation_id} with not found result."""

        reservation_id = 999
        with patch("src.reservation.router.delete_reservation") as mock_delete:
            mock_delete.return_value = None  # Сервис не нашел и вернул None
            response = client.delete(f"/reservations/{reservation_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert (
                f"Бронирование с id={reservation_id} не найдено"
                in response.json()["detail"]
            )
            mock_delete.assert_called_once_with(mock_db_session, reservation_id)

    def test_delete_reservation_not_found_service_exception(
        self, client, mock_db_session
    ):
        """Test case DELETE /reservations/{reservation_id} with not found exception."""

        from fastapi import HTTPException

        reservation_id = 999
        not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование {reservation_id} не найдено в сервисе",
        )
        with patch("src.reservation.router.delete_reservation") as mock_delete:
            mock_delete.side_effect = not_found_exception
            response = client.delete(f"/reservations/{reservation_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert (
                f"Бронирование {reservation_id} не найдено в сервисе"
                in response.json()["detail"]
            )
            mock_delete.assert_called_once_with(mock_db_session, reservation_id)

    def test_delete_reservation_service_error(self, client, mock_db_session):
        """Test case DELETE /reservations/{reservation_id} with service error."""

        reservation_id = 1
        with patch("src.reservation.router.delete_reservation") as mock_delete:
            mock_delete.side_effect = Exception("Deletion error")
            with pytest.raises(Exception) as exc_info:
                client.delete(f"/reservations/{reservation_id}")
            assert "Deletion error" in str(exc_info.value)
            mock_delete.assert_called_once_with(mock_db_session, reservation_id)

    def test_delete_reservation_invalid_id_type(self, client):
        """Test case DELETE /reservations/{reservation_id} with invalid ID type."""

        response = client.delete("/reservations/abc")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
