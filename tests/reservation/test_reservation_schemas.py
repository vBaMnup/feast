from datetime import datetime

import pytest
from pydantic import ValidationError

from src.reservation.schemas import Reservation, ReservationCreate, ReservationBase


class TestReservationPydanticModels:
    """Test ReservationPydanticModels."""

    def test_reservation_base_with_valid_data(self):
        """
        Test for creating a ReservationBase with valid data.
        """

        reservation_time = datetime(2025, 4, 10, 18, 0)
        reservation = ReservationBase(
            customer_name="Иванов Иван",
            table_id=1,
            reservation_time=reservation_time,
            duration_minutes=120,
        )

        assert reservation.customer_name == "Иванов Иван"
        assert reservation.table_id == 1
        assert reservation.reservation_time == reservation_time
        assert reservation.duration_minutes == 120

    def test_reservation_create_with_valid_data(self):
        """
        Test for creating a ReservationCreate with valid data.
        """

        reservation_time = datetime(2025, 4, 10, 19, 30)
        reservation = ReservationCreate(
            customer_name="Петров Петр",
            table_id=2,
            reservation_time=reservation_time,
            duration_minutes=90,
        )

        assert reservation.customer_name == "Петров Петр"
        assert reservation.table_id == 2
        assert reservation.reservation_time == reservation_time
        assert reservation.duration_minutes == 90

    def test_reservation_schema_with_valid_data(self):
        """
        Test for creating a Reservation with valid data.
        """

        reservation_time = datetime(2025, 4, 11, 12, 0)
        reservation_data = {
            "id": 1,
            "customer_name": "Сидоров Сидор",
            "table_id": 3,
            "reservation_time": reservation_time,
            "duration_minutes": 60,
        }

        reservation = Reservation(**reservation_data)

        assert reservation.id == 1
        assert reservation.customer_name == "Сидоров Сидор"
        assert reservation.table_id == 3
        assert reservation.reservation_time == reservation_time
        assert reservation.duration_minutes == 60

    def test_reservation_from_orm(self):
        """
        Test for creating a Reservation from an ORM object.
        """

        class OrmReservation:
            id = 2
            customer_name = "Смирнова Анна"
            table_id = 4
            reservation_time = datetime(2025, 4, 12, 20, 0)
            duration_minutes = 180

        orm_obj = OrmReservation()
        reservation = Reservation.model_validate(orm_obj, from_attributes=True)

        assert reservation.id == 2
        assert reservation.customer_name == "Смирнова Анна"
        assert reservation.table_id == 4
        assert reservation.reservation_time == datetime(2025, 4, 12, 20, 0)
        assert reservation.duration_minutes == 180

    # Тесты для Edge cases

    def test_empty_customer_name(self):
        """
        Test creating a reservation with an empty customer name.
        """

        reservation_time = datetime(2025, 4, 10, 18, 0)
        reservation = ReservationBase(
            customer_name="",
            table_id=1,
            reservation_time=reservation_time,
            duration_minutes=120,
        )

        assert reservation.customer_name == ""

    def test_minimum_duration(self):
        """
        Test creating a reservation with a minimum duration.
        """

        reservation_time = datetime(2025, 4, 10, 18, 0)
        reservation = ReservationBase(
            customer_name="Краткий визит",
            table_id=1,
            reservation_time=reservation_time,
            duration_minutes=1,
        )

        assert reservation.duration_minutes == 1

    def test_zero_duration(self):
        """
        Test creating a reservation with a zero duration.
        """

        reservation_time = datetime(2025, 4, 10, 18, 0)
        reservation = ReservationBase(
            customer_name="Тестовый клиент",
            table_id=1,
            reservation_time=reservation_time,
            duration_minutes=0,
        )

        assert reservation.duration_minutes == 0

    def test_negative_duration(self):
        """
        Test creating a reservation with a negative duration.
        """

        reservation_time = datetime(2025, 4, 10, 18, 0)
        reservation = ReservationBase(
            customer_name="Тестовый клиент",
            table_id=1,
            reservation_time=reservation_time,
            duration_minutes=-30,
        )

        assert reservation.duration_minutes == -30

    def test_very_long_duration(self):
        """
        Test creating a reservation with a very long duration.
        """

        reservation_time = datetime(2025, 4, 10, 18, 0)
        reservation = ReservationBase(
            customer_name="VIP Клиент",
            table_id=5,
            reservation_time=reservation_time,
            duration_minutes=1440,  # 24 часа
        )

        assert reservation.duration_minutes == 1440

    def test_past_date(self):
        """
        Test creating a reservation with a past date.
        """

        past_time = datetime(2020, 1, 1, 12, 0)
        reservation = ReservationBase(
            customer_name="Исторический клиент",
            table_id=1,
            reservation_time=past_time,
            duration_minutes=60,
        )

        assert reservation.reservation_time == past_time

    def test_future_date(self):
        """
        Test creating a reservation with a future date.
        """

        future_time = datetime(2030, 12, 31, 23, 59)
        reservation = ReservationBase(
            customer_name="Футуристический клиент",
            table_id=1,
            reservation_time=future_time,
            duration_minutes=60,
        )

        assert reservation.reservation_time == future_time

    def test_very_long_customer_name(self):
        """
        Test creating a reservation with a very long customer name.
        """

        very_long_name = "А" * 1000
        reservation_time = datetime(2025, 4, 10, 18, 0)
        reservation = ReservationBase(
            customer_name=very_long_name,
            table_id=1,
            reservation_time=reservation_time,
            duration_minutes=60,
        )

        assert reservation.customer_name == very_long_name
        assert len(reservation.customer_name) == 1000

    # Тесты для Invalid inputs

    def test_missing_required_customer_name(self):
        """
        Test creating a reservation without a customer name.
        """

        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(
                table_id=1,
                reservation_time=datetime(2025, 4, 10, 18, 0),
                duration_minutes=60,
            )

        error_details = exc_info.value.errors()
        assert len(error_details) == 1
        assert error_details[0]["loc"] == ("customer_name",)
        assert "Field required" in error_details[0]["msg"]

    def test_missing_required_table_id(self):
        """
        Test creating a reservation without a table id.
        """

        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(
                customer_name="Иванов Иван",
                reservation_time=datetime(2025, 4, 10, 18, 0),
                duration_minutes=60,
            )

        error_details = exc_info.value.errors()
        assert len(error_details) == 1
        assert error_details[0]["loc"] == ("table_id",)
        assert "Field required" in error_details[0]["msg"]

    def test_missing_required_reservation_time(self):
        """
        Test creating a reservation without a reservation time.
        """

        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(
                customer_name="Иванов Иван", table_id=1, duration_minutes=60
            )

        error_details = exc_info.value.errors()
        assert len(error_details) == 1
        assert error_details[0]["loc"] == ("reservation_time",)
        assert "Field required" in error_details[0]["msg"]

    def test_missing_required_duration_minutes(self):
        """
        Test creating a reservation without a duration.
        """

        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(
                customer_name="Иванов Иван",
                table_id=1,
                reservation_time=datetime(2025, 4, 10, 18, 0),
            )

        error_details = exc_info.value.errors()
        assert len(error_details) == 1
        assert error_details[0]["loc"] == ("duration_minutes",)
        assert "Field required" in error_details[0]["msg"]

    def test_wrong_type_for_customer_name(self):
        """
        Test creating a reservation with a wrong type for customer_name.
        """

        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(
                customer_name=123,
                table_id=1,
                reservation_time=datetime(2025, 4, 10, 18, 0),
                duration_minutes=60,
            )

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("customer_name",)
        assert "Input should be a valid string" in error_details[0]["msg"]

    def test_wrong_type_for_table_id(self):
        """
        Test creating a reservation with a wrong type for table_id.
        """

        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(
                customer_name="Иванов Иван",
                table_id="один",
                reservation_time=datetime(2025, 4, 10, 18, 0),
                duration_minutes=60,
            )

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("table_id",)
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in error_details[0]["msg"]
        )

    def test_wrong_type_for_reservation_time(self):
        """
        Test creating a reservation with a wrong type for reservation_time.
        """

        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(
                customer_name="Иванов Иван",
                table_id=1,
                reservation_time="10.04.2025 18:00",
                duration_minutes=60,
            )

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("reservation_time",)

    def test_wrong_type_for_duration_minutes(self):
        """
        Test creating a reservation with a wrong type for duration_minutes.
        """

        with pytest.raises(ValidationError) as exc_info:
            ReservationBase(
                customer_name="Иванов Иван",
                table_id=1,
                reservation_time=datetime(2025, 4, 10, 18, 0),
                duration_minutes="шестьдесят",
            )

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("duration_minutes",)
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in error_details[0]["msg"]
        )

    def test_missing_id_in_reservation_schema(self):
        """
        Test creating a reservation without an id.
        """

        with pytest.raises(ValidationError) as exc_info:
            Reservation(
                customer_name="Иванов Иван",
                table_id=1,
                reservation_time=datetime(2025, 4, 10, 18, 0),
                duration_minutes=60,
            )

        error_details = exc_info.value.errors()
        assert len(error_details) == 1
        assert error_details[0]["loc"] == ("id",)
        assert "Field required" in error_details[0]["msg"]

    def test_wrong_type_for_id(self):
        """
        Test creating a reservation with a wrong type for id.
        """

        with pytest.raises(ValidationError) as exc_info:
            Reservation(
                id="один",
                customer_name="Иванов Иван",
                table_id=1,
                reservation_time=datetime(2025, 4, 10, 18, 0),
                duration_minutes=60,
            )

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("id",)
        assert (
            "Input should be a valid integer, unable to parse string as an integer"
            in error_details[0]["msg"]
        )

    def test_string_datetime_conversion(self):
        """
        Test converting a string datetime to a datetime object.
        """

        reservation = ReservationBase(
            customer_name="Иванов Иван",
            table_id=1,
            reservation_time="2025-04-10T18:00:00",
            duration_minutes=60,
        )

        assert isinstance(reservation.reservation_time, datetime)
        assert reservation.reservation_time == datetime(2025, 4, 10, 18, 0)
