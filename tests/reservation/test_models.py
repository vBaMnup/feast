import pytest
from sqlalchemy.exc import IntegrityError, DataError

from src.reservation.models import Table


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
