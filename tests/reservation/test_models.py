import datetime
import time
from datetime import timezone

import pytest
from sqlalchemy.exc import IntegrityError, DataError

from src.reservation.models import Table, Reservation


class TestTableModel:
    """Tests for Table model."""

    def test_create_table_with_valid_data(self, setup_database):
        """
        Test for creating a table with valid data.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_table = Table(name="Стол у окна", seats=4, location="Зал 1")
        session.add(test_table)
        session.commit()

        assert test_table.id is not None
        assert test_table.name == "Стол у окна"
        assert test_table.seats == 4
        assert test_table.location == "Зал 1"

        retrieved_table = session.query(Table).filter_by(id=test_table.id).first()
        assert retrieved_table is not None
        assert retrieved_table.name == "Стол у окна"

    def test_repr_method(self):
        """
        Test for the __repr__ method.
        """

        table = Table(id=1, name="VIP столик", seats=6, location="VIP зона")
        expected_repr = "<Table(id=1, name='VIP столик', seats=6, location='VIP зона')>"

        assert repr(table) == expected_repr

    def test_null_name(self, setup_database):
        """
        Test for creating a table with a null name.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_table = Table(seats=4, location="Зал 1")
        session.add(test_table)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

    def test_null_seats(self, setup_database):
        """
        Test for creating a table with a null number of seats.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_table = Table(name="Стол у окна", location="Зал 1")
        session.add(test_table)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

    def test_null_location(self, setup_database):
        """
        Test for creating a table with a null location.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_table = Table(name="Стол у окна", seats=4)
        session.add(test_table)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

    def test_negative_seats(self, setup_database):
        """
        Test for creating a table with a negative number of seats.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_table = Table(name="Стол у окна", seats=-4, location="Зал 1")
        session.add(test_table)

        session.commit()

        retrieved_table = session.query(Table).filter_by(id=test_table.id).first()
        assert retrieved_table.seats == -4

    def test_empty_string_fields(self, setup_database):
        """
        Test for creating a table with empty string fields.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_table = Table(name="", seats=4, location="")
        session.add(test_table)

        session.commit()

        retrieved_table = session.query(Table).filter_by(id=test_table.id).first()
        assert retrieved_table.name == ""
        assert retrieved_table.location == ""

    def test_very_long_strings(self, setup_database):
        """
        Test for creating a table with very long strings.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        very_long_name = "A" * 1000
        very_long_location = "B" * 1000

        test_table = Table(name=very_long_name, seats=4, location=very_long_location)
        session.add(test_table)

        try:
            session.commit()

            retrieved_table = session.query(Table).filter_by(id=test_table.id).first()
            assert len(retrieved_table.name) == 1000
            assert len(retrieved_table.location) == 1000
        except DataError:
            session.rollback()
            pytest.skip("База данных не поддерживает очень длинные строки")

    def test_zero_seats(self, setup_database):
        """
        Test for creating a table with zero seats.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_table = Table(name="Декоративный стол", seats=0, location="Фойе")
        session.add(test_table)
        session.commit()

        retrieved_table = session.query(Table).filter_by(id=test_table.id).first()
        assert retrieved_table.seats == 0

    def test_duplicate_table_name(self, setup_database):
        """
        Test for creating a table with a duplicate name.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        table1 = Table(name="Стол №1", seats=4, location="Зал 1")
        session.add(table1)
        session.commit()

        table2 = Table(name="Стол №1", seats=2, location="Зал 2")
        session.add(table2)
        session.commit()

        tables = session.query(Table).filter_by(name="Стол №1").all()
        assert len(tables) == 2
        assert tables[0].id != tables[1].id


class TestReservationModel:
    """Test class for the Reservation model."""

    def test_create_reservation_with_valid_data(
        self, setup_database, create_test_table
    ):
        """
        Test for creating a reservation with valid data.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        now = datetime.datetime.now(datetime.UTC)

        test_reservation = Reservation(
            customer_name="Иван Иванов",
            table_id=table.id,
            reservation_time=now,
            duration_minutes=60,
        )
        reservation_time_aware = test_reservation.reservation_time.replace(
            tzinfo=timezone.utc
        )
        session.add(test_reservation)
        session.commit()

        assert test_reservation.id is not None
        assert test_reservation.customer_name == "Иван Иванов"
        assert test_reservation.table_id == table.id
        assert test_reservation.duration_minutes == 60
        assert abs((reservation_time_aware - now).total_seconds()) < 1

        assert test_reservation.table.id == table.id
        assert test_reservation.table.name == "Тестовый стол"

    def test_default_reservation_time(self, setup_database, create_test_table):
        """
        Test for creating a reservation without specifying reservation_time.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        test_reservation = Reservation(
            customer_name="Петр Петров", table_id=table.id, duration_minutes=30
        )

        before_save = datetime.datetime.now(datetime.timezone.utc).replace(
            microsecond=0
        )
        session.add(test_reservation)
        session.commit()
        time.sleep(0.1)
        after_save = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)

        reservation_time_aware = test_reservation.reservation_time.replace(
            microsecond=0
        )

        assert reservation_time_aware is not None
        assert before_save <= reservation_time_aware <= after_save

    def test_repr_method(self, create_test_table):
        """
        Test for the __repr__ method of the Reservation class.

        Args:
            create_test_table (fixture): Fixture for creating a test table.
        """

        fixed_time = datetime.datetime(2023, 5, 10, 12, 0, tzinfo=datetime.UTC)

        reservation = Reservation(
            id=1,
            customer_name="Сергей Сергеев",
            table_id=create_test_table.id,
            reservation_time=fixed_time,
            duration_minutes=90,
        )

        expected_repr = (
            f"<Reservation(id=1, customer_name='Сергей Сергеев', "
            f"table_id={create_test_table.id}, reservation_time={fixed_time}, "
            f"duration_minutes=90)>"
        )

        assert repr(reservation) == expected_repr

    def test_null_customer_name(self, setup_database, create_test_table):
        """
        Test for creating a reservation without a customer name.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        test_reservation = Reservation(table_id=table.id, duration_minutes=45)
        session.add(test_reservation)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

    def test_null_table_id(self, setup_database):
        """
        Test for creating a reservation without a table ID.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_reservation = Reservation(
            customer_name="Андрей Андреев", duration_minutes=60
        )
        session.add(test_reservation)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

    def test_null_duration(self, setup_database, create_test_table):
        """
        Test for creating a reservation without a duration.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        test_reservation = Reservation(customer_name="Елена Еленина", table_id=table.id)
        session.add(test_reservation)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

    def test_non_existent_table_id(self, setup_database):
        """
        Test for creating a reservation with a non-existent table ID.

        Args:
            setup_database (fixture): Fixture for setting up the database.
        """

        session = setup_database

        test_reservation = Reservation(
            customer_name="Ольга Ольгина", table_id=999, duration_minutes=120
        )
        session.add(test_reservation)

        with pytest.raises(IntegrityError):
            session.commit()

        session.rollback()

    def test_zero_duration(self, setup_database, create_test_table):
        """
        Test for creating a reservation with a zero duration.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        test_reservation = Reservation(
            customer_name="Дмитрий Дмитриев", table_id=table.id, duration_minutes=0
        )
        session.add(test_reservation)
        session.commit()

        retrieved_reservation = (
            session.query(Reservation).filter_by(id=test_reservation.id).first()
        )
        assert retrieved_reservation.duration_minutes == 0

    def test_negative_duration(self, setup_database, create_test_table):
        """
        Test for creating a reservation with a negative duration.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        test_reservation = Reservation(
            customer_name="Анна Анина", table_id=table.id, duration_minutes=-30
        )
        session.add(test_reservation)

        session.commit()

        retrieved_reservation = (
            session.query(Reservation).filter_by(id=test_reservation.id).first()
        )
        assert retrieved_reservation.duration_minutes == -30

    def test_long_customer_name(self, setup_database, create_test_table):
        """
        Test for creating a reservation with a long customer name.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        very_long_name = "А" * 1000

        test_reservation = Reservation(
            customer_name=very_long_name, table_id=table.id, duration_minutes=45
        )
        session.add(test_reservation)

        try:
            session.commit()

            retrieved_reservation = (
                session.query(Reservation).filter_by(id=test_reservation.id).first()
            )
            assert len(retrieved_reservation.customer_name) == 1000
        except DataError:
            session.rollback()
            pytest.skip("База данных не поддерживает очень длинные строки")

    def test_past_reservation_time(self, setup_database, create_test_table):
        """
        Test for creating a reservation with a past reservation time.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        past_time = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)

        test_reservation = Reservation(
            customer_name="Максим Максимов",
            table_id=table.id,
            reservation_time=past_time,
            duration_minutes=60,
        )
        session.add(test_reservation)
        session.commit()

        retrieved_reservation = (
            session.query(Reservation).filter_by(id=test_reservation.id).first()
        )
        time_diff = abs(
            (retrieved_reservation.reservation_time - past_time).total_seconds()
        )
        assert time_diff < 1

    def test_future_reservation_time(self, setup_database, create_test_table):
        """
        Test for creating a reservation with a future reservation time.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        future_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=7)

        test_reservation = Reservation(
            customer_name="Юлия Юлина",
            table_id=table.id,
            reservation_time=future_time,
            duration_minutes=120,
        )
        session.add(test_reservation)
        session.commit()

        retrieved_reservation = (
            session.query(Reservation).filter_by(id=test_reservation.id).first()
        )
        time_diff = abs(
            (retrieved_reservation.reservation_time - future_time).total_seconds()
        )
        assert time_diff < 1

    def test_backref_relationship(self, setup_database, create_test_table):
        """
        Test for backref relationship.

        Args:
            setup_database (fixture): Fixture for setting up the database.
            create_test_table (fixture): Fixture for creating a test table.
        """

        session = setup_database
        table = create_test_table

        reservation1 = Reservation(
            customer_name="Клиент 1", table_id=table.id, duration_minutes=60
        )

        reservation2 = Reservation(
            customer_name="Клиент 2", table_id=table.id, duration_minutes=90
        )

        session.add_all([reservation1, reservation2])
        session.commit()

        session.refresh(table)

        assert len(table.reservations) == 2
        assert table.reservations[0].customer_name in ["Клиент 1", "Клиент 2"]
        assert table.reservations[1].customer_name in ["Клиент 1", "Клиент 2"]

        for reservation in table.reservations:
            assert reservation.table_id == table.id
            assert reservation.table.name == "Тестовый стол"
