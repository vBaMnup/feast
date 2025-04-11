from unittest.mock import patch, MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.tables.models import Table as TableModel
from src.tables.schemas import TableCreate
from src.tables.service import (
    get_tables,
    create_table,
    delete_table,
)


class TestTableCRUD:
    """Tests for Table CRUD operations."""

    MOCK_TABLE_DATA = {"id": 1, "name": "Стол у окна", "seats": 4, "location": "Зал 1"}

    def setup_mock_db(self, return_value):
        """Setup mock database session."""

        mock_db = MagicMock(spec=Session)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = return_value
        mock_result.scalars.return_value.all.return_value = return_value
        mock_db.execute.return_value = mock_result
        return mock_db

    @pytest.mark.parametrize(
        "skip, limit, expected_calls",
        [(0, 100, (0, 100)), (1, 1, (1, 1)), (-10, 100, (-10, 100)), (0, 0, (0, 0))],
    )
    def test_get_tables_pagination(self, skip, limit, expected_calls):
        """Test getting tables with pagination."""

        expected_tables = [TableModel(**self.MOCK_TABLE_DATA)]
        with patch("src.tables.service.select") as mock_select:
            mock_db = MagicMock(spec=Session)
            mock_db.execute.return_value.scalars.return_value.all.return_value = (
                expected_tables
            )

            result = get_tables(mock_db, skip=skip, limit=limit)

            mock_select.return_value.offset.assert_called_once_with(expected_calls[0])
            mock_select.return_value.offset.return_value.limit.assert_called_once_with(
                expected_calls[1]
            )
            assert result == expected_tables

    def test_get_tables_empty(self):
        """Test getting an empty list of tables."""

        with patch("src.tables.service.select"):
            mock_db = self.setup_mock_db([])
            result = get_tables(mock_db)
            assert result == []

    def test_create_table_success(self):
        """Test successful table creation."""

        table_data = TableCreate(name="Новый стол", seats=8, location="VIP зона")
        with patch("src.tables.utils.Table") as mock_model:
            mock_db = MagicMock(spec=Session)
            mock_instance = mock_model.return_value
            mock_instance.id = 1

            result = create_table(mock_db, table_data)

            mock_model.assert_called_with(**table_data.model_dump(exclude_none=True))
            mock_db.add.assert_called_with(mock_instance)
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_with(mock_instance)
            assert result == mock_instance

    def test_create_table_error(self):
        """Test error during table creation."""

        mock_db = MagicMock(spec=Session)
        mock_db.add.side_effect = SQLAlchemyError("Ошибка")

        with pytest.raises(HTTPException) as exc:
            create_table(mock_db, TableCreate(name="Test", seats=2))

        assert exc.value.status_code == 500

    def test_delete_table_success(self):
        """Test successful table deletion."""

        mock_table = MagicMock(spec=TableModel)
        mock_db = MagicMock(spec=Session)

        mock_db.get.return_value = mock_table

        with patch("src.tables.service.delete_table", return_value=mock_table):
            result = delete_table(mock_db, 1)

            mock_db.get.assert_called_with(TableModel, 1)

            mock_db.delete.assert_called_with(mock_table)

            mock_db.commit.assert_called_once()

            assert result == mock_table

    def test_delete_table_not_found(self):
        """Test deleting a non-existent table."""

        mock_db = MagicMock(spec=Session)
        mock_db.get.return_value = None

        with pytest.raises(HTTPException) as exc:
            delete_table(mock_db, 1)

        assert exc.value.status_code == 404
