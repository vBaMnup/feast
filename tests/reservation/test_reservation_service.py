from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.reservation import models, schemas
from src.reservation.service import (
    get_reservations,
    create_reservation,
    delete_reservation,
)


class TestReservationCRUD:
    """Tests class for reservation service."""

    MOCK_RESERVATION_DATA = {
        "id": 1,
        "customer_name": "Иванов Иван",
        "table_id": 1,
        "reservation_time": datetime(2025, 4, 10, 18, 0),
        "duration_minutes": 60,
    }

    def setup_mock_db(self, return_value=None):
        """Setup mock database session."""
        mock_db = MagicMock(spec=Session)
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = return_value or []
        mock_db.execute.return_value = mock_result
        return mock_db

    def test_get_reservations_default_params(self):
        """Test getting reservations with default parameters."""

        mock_db = MagicMock(spec=Session)
        expected_reservations = [models.Reservation(**self.MOCK_RESERVATION_DATA)]
        mock_db.scalars.return_value.all.return_value = expected_reservations

        with patch("src.reservation.service.select") as mock_select:
            result = get_reservations(mock_db)

        mock_select.assert_called_once()
        mock_select.return_value.offset.assert_called_once_with(0)
        mock_select.return_value.offset.return_value.limit.assert_called_once_with(100)
        assert result == expected_reservations

    @pytest.mark.parametrize("skip, limit", [(5, 10), (0, 0), (-1, 5)])
    def test_get_reservations_pagination(self, skip, limit):
        """Test getting reservations with pagination"""

        mock_db = MagicMock(spec=Session)
        expected_reservations = [models.Reservation(**self.MOCK_RESERVATION_DATA)]
        mock_db.scalars.return_value.all.return_value = expected_reservations

        with patch("src.reservation.service.select") as mock_select:
            result = get_reservations(mock_db, skip=skip, limit=limit)

        mock_select.return_value.offset.assert_called_once_with(skip)
        mock_select.return_value.offset.return_value.limit.assert_called_once_with(
            limit
        )
        assert result == expected_reservations

    def test_get_reservations_empty(self):
        """Test getting reservations with empty result"""

        mock_db = MagicMock(spec=Session)
        mock_db.scalars.return_value.all.return_value = []

        with patch("src.reservation.service.select") as mock_select:
            result = get_reservations(mock_db)

        mock_select.assert_called_once()
        mock_select.return_value.offset.assert_called_once_with(0)
        mock_select.return_value.offset.return_value.limit.assert_called_once_with(100)
        assert result == []

    def test_create_reservation_success(self):
        """Test successful reservation creation"""

        mock_db = MagicMock(spec=Session)
        reservation_in = schemas.ReservationCreate(
            customer_name="Иванов Иван",
            table_id=1,
            reservation_time=datetime(2025, 6, 10, 18, 0),
            duration_minutes=60,
        )
        expected_reservation = models.Reservation(
            id=1,
            customer_name="Иванов Иван",
            table_id=1,
            reservation_time=datetime(2025, 6, 10, 18, 0),
            duration_minutes=60,
        )
        mock_db.commit.return_value = None
        mock_db.scalar.return_value = None

        mock_db.add.return_value = None
        mock_db.refresh.return_value = None

        with patch(
            "src.reservation.models.Reservation", return_value=expected_reservation
        ) as mock_reservation:
            mock_reservation.reservation_time = datetime(2025, 4, 10, 18, 0)
            mock_reservation.duration_minutes = 60

            result = create_reservation(mock_db, reservation_in)

        assert result == expected_reservation
        mock_db.commit.assert_called_once()

    def test_create_reservation_conflict(self):
        """Test reservation creation with conflict"""

        mock_db = MagicMock(spec=Session)
        reservation_in = schemas.ReservationCreate(
            customer_name="Иванов Иван",
            table_id=1,
            reservation_time=datetime(2025, 6, 10, 18, 0),
            duration_minutes=60,
        )

        with patch("src.reservation.service.create_reservation", return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                create_reservation(mock_db, reservation_in)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "Конфликт бронирования" in exc_info.value.detail

    def test_create_reservation_database_error(self):
        """Test reservation creation with database error"""

        mock_db = MagicMock(spec=Session)
        reservation_in = schemas.ReservationCreate(
            customer_name="Ошибка",
            table_id=1,
            reservation_time=datetime(2025, 6, 10, 18, 0),
            duration_minutes=60,
        )
        mock_db.commit.side_effect = SQLAlchemyError("Ошибка БД")

        with pytest.raises(HTTPException) as exc_info:
            create_reservation(mock_db, reservation_in)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT

    def test_delete_reservation_success(self):
        """Test successful reservation deletion"""

        mock_reservation = MagicMock(spec=models.Reservation)
        mock_db = MagicMock(spec=Session)
        mock_db.scalar.return_value = mock_reservation

        result = delete_reservation(mock_db, 1)

        mock_db.delete.assert_called_once_with(mock_reservation)
        mock_db.commit.assert_called_once()
        assert result is None

    def test_delete_reservation_not_found(self):
        """Test reservation deletion with not found"""

        mock_db = MagicMock(spec=Session)
        mock_db.scalar.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            delete_reservation(mock_db, 999)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "не найдено" in exc_info.value.detail
        mock_db.delete.assert_not_called()

    def test_delete_reservation_database_error(self):
        """Test reservation deletion with database error"""

        mock_db = MagicMock(spec=Session)
        mock_db.commit.side_effect = SQLAlchemyError("Ошибка удаления")
        mock_db.scalar.return_value = MagicMock(spec=models.Reservation)

        mock_db.query.return_value.filter.return_value.one_or_none.return_value = (
            MagicMock(spec=models.Reservation)
        )

        with pytest.raises(HTTPException) as exc_info:
            delete_reservation(mock_db, 1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Ошибка удаления бронирования: Ошибка удаления"

    @pytest.mark.parametrize("duration", [-30, 0, 1440])
    def test_create_reservation_edge_durations(self, duration):
        """Test creating reservation with edge durations"""

        mock_db = MagicMock(spec=Session)
        reservation_in = schemas.ReservationCreate(
            customer_name="Тест",
            table_id=1,
            reservation_time=datetime(2025, 6, 10, 18, 0),
            duration_minutes=duration,
        )

        mock_db.scalar.return_value = None

        if duration <= 0:
            with pytest.raises(HTTPException) as exc_info:
                create_reservation(mock_db, reservation_in)
            mock_db.commit.assert_not_called()
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        else:
            mock_db.add.return_value = None
            mock_db.flush.return_value = None

            def side_effect_add(obj):
                obj.id = 1
                return None

            mock_db.add.side_effect = side_effect_add

            result = create_reservation(mock_db, reservation_in)

            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            assert result.id == 1
            assert result.customer_name == "Тест"
            assert result.table_id == 1
            assert result.reservation_time == datetime(2025, 6, 10, 18, 0)
            assert result.duration_minutes == duration

    def test_create_reservation_past_date(self):
        """Test creating reservation with past date"""

        mock_db = MagicMock(spec=Session)
        reservation_in = schemas.ReservationCreate(
            customer_name="Тест",
            table_id=1,
            reservation_time=datetime(2020, 1, 1, 12, 0),
            duration_minutes=60,
        )

        with pytest.raises(HTTPException) as exc_info:
            create_reservation(mock_db, reservation_in)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert exc_info.value.detail == "Время бронирования не может быть в прошлом."

        mock_db.commit.assert_not_called()

    def test_create_reservation_invalid_table_id(self):
        """Test creating reservation with invalid table ID"""

        mock_db = MagicMock(spec=Session)
        reservation_in = schemas.ReservationCreate(
            customer_name="Несуществующий стол",
            table_id=999,
            reservation_time=datetime(2025, 6, 10, 18, 0),
            duration_minutes=60,
        )

        mock_db.scalar.return_value = None

        mock_db.get.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            result = create_reservation(mock_db, reservation_in)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert f"Стол с ID {reservation_in.table_id} не найден" in exc_info.value.detail

        mock_db.commit.assert_not_called()
