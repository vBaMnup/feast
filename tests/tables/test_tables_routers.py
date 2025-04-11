from unittest.mock import patch

import pytest
from fastapi import status

from src.tables import schemas

MOCK_TABLE_DATA = {
    "id": 1,
    "name": "Стол у окна",
    "seats": 4,
    "location": "Зал 1",
}
MOCK_TABLE_OBJ = schemas.Table(**MOCK_TABLE_DATA)

MOCK_TABLE_CREATE_DATA = {
    "name": "Большой стол",
    "seats": 10,
    "location": "Банкетный зал",
}


class TestReadTables:
    """Test case GET /tables/"""

    def test_read_tables_default(self, client):
        """Test case GET /tables/ with default parameters."""

        with patch("src.tables.router.get_tables") as mock_get:
            mock_get.return_value = [MOCK_TABLE_OBJ]
            response = client.get("/tables/")

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == [MOCK_TABLE_DATA]
            mock_get.assert_called_once()
            assert mock_get.call_args[0][1] == 0
            assert mock_get.call_args[0][2] == 100

    @pytest.mark.parametrize("skip, limit", [(5, 10), (0, 50), (10, 0)])
    def test_read_tables_pagination(self, client, skip, limit):
        """Test case GET /tables/ with pagination."""

        with patch("src.tables.router.get_tables") as mock_get:
            mock_get.return_value = []
            response = client.get(f"/tables/?skip={skip}&limit={limit}")

            assert response.status_code == status.HTTP_200_OK
            mock_get.assert_called_once()
            assert mock_get.call_args[0][1] == skip
            assert mock_get.call_args[0][2] == limit

    def test_read_tables_empty(self, client):
        """Test case GET /tables/ with empty result."""

        with patch("src.tables.router.get_tables") as mock_get:
            mock_get.return_value = []
            response = client.get("/tables/")

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == []
            mock_get.assert_called_once()

    def test_read_tables_service_error(self, client):
        """Test case GET /tables/ with service error."""

        with patch("src.tables.router.get_tables") as mock_get:
            mock_get.side_effect = Exception("Database error")
            with pytest.raises(Exception) as exc_info:
                client.get("/tables/")
            assert "Database error" in str(exc_info.value)


class TestCreateTable:
    """Test case POST /tables/"""

    def test_create_table_success(self, client):
        """Test case POST /tables/ with success result."""

        created_table_obj = schemas.Table(id=2, **MOCK_TABLE_CREATE_DATA)
        with patch("src.tables.router.create_table") as mock_create:
            mock_create.return_value = created_table_obj
            response = client.post("/tables/", json=MOCK_TABLE_CREATE_DATA)

            assert response.status_code == status.HTTP_201_CREATED
            expected_json = {"id": 2, **MOCK_TABLE_CREATE_DATA}
            assert response.json() == expected_json
            mock_create.assert_called_once()
            call_args = mock_create.call_args[0]
            assert isinstance(call_args[1], schemas.TableCreate)
            assert call_args[1].name == MOCK_TABLE_CREATE_DATA["name"]
            assert call_args[1].seats == MOCK_TABLE_CREATE_DATA["seats"]

    def test_create_table_validation_error_negative_seats(self, client):
        """Test case POST /tables/ with validation error."""

        invalid_data = MOCK_TABLE_CREATE_DATA.copy()
        invalid_data["seats"] = -2
        response = client.post("/tables/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()

    def test_create_table_missing_field(self, client):
        """Test case POST /tables/ with missing field."""

        invalid_data = MOCK_TABLE_CREATE_DATA.copy()
        del invalid_data["name"]
        response = client.post("/tables/", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()

    def test_create_table_service_error(self, client):
        """Test case POST /tables/ with service error."""

        with patch("src.tables.router.create_table") as mock_create:
            mock_create.side_effect = Exception("Service error")
            with pytest.raises(Exception) as exc_info:
                client.post("/tables/", json=MOCK_TABLE_CREATE_DATA)
            assert "Service error" in str(exc_info.value)


class TestDeleteTable:
    """Test case DELETE /tables/{table_id}"""

    def test_delete_table_success(self, client, mock_db_session):
        """Test case DELETE /tables/{table_id} with success result."""

        with patch("src.tables.router.delete_table") as mock_delete:
            mock_delete.return_value = MOCK_TABLE_OBJ
            table_id = MOCK_TABLE_OBJ.id
            response = client.delete(f"/tables/{table_id}")

            assert response.status_code == status.HTTP_200_OK
            assert response.json() == MOCK_TABLE_DATA
            mock_delete.assert_called_once_with(mock_db_session, table_id)

    def test_delete_table_not_found_router_logic(self, client, mock_db_session):
        """Test case DELETE /tables/{table_id} with not found result."""

        table_id = 999
        with patch("src.tables.router.delete_table") as mock_delete:
            mock_delete.return_value = None
            response = client.delete(f"/tables/{table_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert f"Столик с id={table_id} не найден" in response.json()["detail"]
            mock_delete.assert_called_once_with(mock_db_session, table_id)

    def test_delete_table_not_found_service_exception(self, client, mock_db_session):
        """Test case DELETE /tables/{table_id} with not found exception."""

        from fastapi import HTTPException

        table_id = 998
        not_found_exception = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Стол {table_id} не найден в сервисе",
        )
        with patch("src.tables.router.delete_table") as mock_delete:
            mock_delete.side_effect = not_found_exception
            response = client.delete(f"/tables/{table_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert f"Стол {table_id} не найден в сервисе" in response.json()["detail"]
            mock_delete.assert_called_once_with(mock_db_session, table_id)

    def test_delete_table_service_error(self, client, mock_db_session):
        """Test case DELETE /tables/{table_id} with service error."""

        table_id = 1
        with patch("src.tables.router.delete_table") as mock_delete:
            mock_delete.side_effect = Exception("Deletion error")
            with pytest.raises(Exception) as exc_info:
                client.delete(f"/tables/{table_id}")
            assert "Deletion error" in str(exc_info.value)
            mock_delete.assert_called_once_with(mock_db_session, table_id)

    def test_delete_table_invalid_id_type(self, client):
        """Test case DELETE /tables/{table_id} with invalid ID type."""

        response = client.delete("/tables/invalid_id")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
