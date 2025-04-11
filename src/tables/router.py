from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.tables.schemas import Table, TableCreate
from src.tables.service import get_tables, create_table, delete_table

router = APIRouter(prefix="/tables", tags=["Tables"])


@router.get("/", response_model=List[Table])
def read_tables(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get tables with pagination

    Args:
        db: The database session.
        skip: The number of records to skip.
        limit: The maximum number of records to return.

    Returns:
        A list of tables.
    """

    return get_tables(db, skip, limit)


@router.post("/", response_model=Table, status_code=status.HTTP_201_CREATED)
def create_new_table(table_in: TableCreate, db: Session = Depends(get_db)):
    """
    Creating a new table

    Args:
        db: The database session.
        table_in: The table data.

    Returns:
        The created table object.
    """

    return create_table(db, table_in)


@router.delete("/{table_id}", response_model=Table)
def delete_existing_table(table_id: int, db: Session = Depends(get_db)):
    """
    Delete a table.

    Args:
        db: The database session.
        table_id: The ID of the table to delete.

    Returns:
        The deleted table object.
    """

    result = delete_table(db, table_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Столик с id={table_id} не найден."
        )
    return result
