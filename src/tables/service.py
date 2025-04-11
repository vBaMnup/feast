from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.tables.exceptions import create_db_error
from src.tables.models import Table as TableModel
from src.tables.schemas import TableCreate
from src.tables.utils import _create_table_object


def get_tables(db: Session, skip: int = 0, limit: int = 100) -> List[TableModel]:
    """
    Get tables with pagination

    Args:
        db: The database session.
        skip: The number of records to skip.
        limit: The maximum number of records to return.

    Returns:
        A list of tables.
    """

    stmt = select(TableModel).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def create_table(db: Session, table_in: TableCreate) -> TableModel:
    """
    Creating a new table

    Args:
        db: The database session.
        table_in: The table data.

    Returns:
        The created table object.
    """

    try:
        return _create_table_object(db, table_in.model_dump(exclude_none=True))
    except SQLAlchemyError as e:
        db.rollback()
        raise create_db_error("создании", str(e))


def delete_table(db: Session, table_id: int) -> Optional[TableModel]:
    """
    Delete a table.

    Args:
        db: The database session.
        table_id: The ID of the table to delete.

    Returns:
        The deleted table object.
    """

    try:
        db_table = db.get(TableModel, table_id)
        if not db_table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Столик с id={table_id} не найден.",
            )

        db.delete(db_table)
        db.commit()
        return db_table

    except SQLAlchemyError as e:
        db.rollback()
        raise create_db_error("удалении", str(e))
