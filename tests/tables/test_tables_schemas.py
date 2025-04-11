import pytest
from pydantic import ValidationError

from src.tables.schemas import Table, TableBase, TableCreate


class TestTablePydanticModels:
    """Tests for Table Pydantic models."""

    def test_table_base_with_valid_data(self):
        """
        Test creating TableBase with valid data.
        """

        table = TableBase(name="Стол у окна", seats=4, location="Зал 1")

        assert table.name == "Стол у окна"
        assert table.seats == 4
        assert table.location == "Зал 1"

    def test_table_base_with_minimal_data(self):
        """
        Test creating TableBase with minimal data.
        """

        table = TableBase(name="Стол у окна", seats=4)

        assert table.name == "Стол у окна"
        assert table.seats == 4
        assert table.location is None

    def test_table_create_with_valid_data(self):
        """
        Test creating TableCreate with valid data.
        """

        table = TableCreate(name="VIP столик", seats=6, location="VIP зона")

        assert table.name == "VIP столик"
        assert table.seats == 6
        assert table.location == "VIP зона"

    def test_table_schema_with_valid_data(self):
        """
        Test creating Table schema with valid data.
        """

        table_data = {"id": 1, "name": "Стол у окна", "seats": 4, "location": "Зал 1"}

        table = Table(**table_data)

        assert table.id == 1
        assert table.name == "Стол у окна"
        assert table.seats == 4
        assert table.location == "Зал 1"

    def test_table_schema_without_location(self):
        """
        Test creating Table schema without location.
        """

        table_data = {"id": 2, "name": "Стол у окна", "seats": 4}

        table = Table(**table_data)

        assert table.id == 2
        assert table.name == "Стол у окна"
        assert table.seats == 4
        assert table.location is None

    def test_table_from_orm(self):
        """
        Test creating Table schema from ORM object.
        """

        class OrmTable:
            id = 3
            name = "Угловой стол"
            seats = 2
            location = "Угол зала"

        orm_obj = OrmTable()
        table = Table.model_validate(orm_obj)

        assert table.id == 3
        assert table.name == "Угловой стол"
        assert table.seats == 2
        assert table.location == "Угол зала"

    # Тесты для Edge cases

    def test_empty_string_fields(self):
        """
        Test creating a table with empty string fields.
        """

        table = TableBase(name="", seats=4, location="")

        assert table.name == ""
        assert table.seats == 4
        assert table.location == ""

    def test_zero_seats(self):
        """
        Test creating a table with zero seats.
        """

        table = TableBase(name="Декоративный стол", seats=0, location="Фойе")

        assert table.name == "Декоративный стол"
        assert table.seats == 0
        assert table.location == "Фойе"

    def test_negative_seats(self):
        """
        Test creating a table with a negative number of seats.
        """

        table = TableBase(name="Стол у окна", seats=-4, location="Зал 1")

        assert table.name == "Стол у окна"
        assert table.seats == -4
        assert table.location == "Зал 1"

    def test_very_long_strings(self):
        """
        Test creating a table with very long strings.
        """

        very_long_name = "A" * 1000
        very_long_location = "B" * 1000

        table = TableBase(name=very_long_name, seats=4, location=very_long_location)

        assert table.name == very_long_name
        assert len(table.name) == 1000
        assert table.location == very_long_location
        assert len(table.location) == 1000

    def test_missing_required_name(self):
        """
        Test creating a table without a required field name.
        """

        with pytest.raises(ValidationError) as exc_info:
            TableBase(seats=4, location="Зал 1")

        error_details = exc_info.value.errors()
        assert len(error_details) == 1
        assert error_details[0]["loc"] == ("name",)

        assert error_details[0]["msg"] == "Field required"

    def test_missing_required_seats(self):
        """
        Test creating a table without a required field seats.
        """

        with pytest.raises(ValidationError) as exc_info:
            TableBase(name="Стол у окна", location="Зал 1")

        error_details = exc_info.value.errors()
        assert len(error_details) == 1
        assert error_details[0]["loc"] == ("seats",)
        assert error_details[0]["msg"] == "Field required"

    def test_wrong_type_for_name(self):
        """
        Test creating a table with a wrong type for the name field.
        """

        with pytest.raises(ValidationError) as exc_info:
            TableBase(name=123, seats=4, location="Зал 1")

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("name",)
        assert error_details[0]["msg"] == "Input should be a valid string"

    def test_wrong_type_for_seats(self):
        """
        Test creating a table with a wrong type for the seats field.
        """

        with pytest.raises(ValidationError) as exc_info:
            TableBase(name="Стол у окна", seats="четыре", location="Зал 1")

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("seats",)
        assert (
            error_details[0]["msg"]
            == "Input should be a valid integer, unable to parse string as an integer"
        )

    def test_wrong_type_for_location(self):
        """
        Test creating a table with a wrong type for the location field.
        """

        with pytest.raises(ValidationError) as exc_info:
            TableBase(name="Стол у окна", seats=4, location=123)

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("location",)
        assert error_details[0]["msg"] == "Input should be a valid string"

    def test_missing_id_in_table_schema(self):
        """
        Test creating a table without a required field id.
        """

        with pytest.raises(ValidationError) as exc_info:
            Table(name="Стол у окна", seats=4, location="Зал 1")

        error_details = exc_info.value.errors()
        assert len(error_details) == 1
        assert error_details[0]["loc"] == ("id",)
        assert "Field required" in error_details[0]["msg"]

    def test_wrong_type_for_id(self):
        """
        Test creating a table with a wrong type for the id field.
        """

        with pytest.raises(ValidationError) as exc_info:
            Table(id="один", name="Стол у окна", seats=4, location="Зал 1")

        error_details = exc_info.value.errors()
        assert error_details[0]["loc"] == ("id",)
        assert (
            error_details[0]["msg"]
            == "Input should be a valid integer, unable to parse string as an integer"
        )
