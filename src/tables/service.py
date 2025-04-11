from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.tables.models import Table as TableModel
from src.tables.schemas import TableCreate


def get_table(db: Session, table_id: int) -> Optional[TableModel]:
    """
    Gets table by id

    :param db: Database session
    :param table_id: ID of table
    :return: Table
    """

    stmt = select(TableModel).where(TableModel.id == table_id)
    result = db.execute(stmt).scalar_one_or_none()
    return result


def get_tables(db: Session, skip: int = 0, limit: int = 100) -> List[TableModel]:
    """
    Gets all tables

    :param db: Database session
    :param skip: Number of tables to skip
    :param limit: Number of tables to return
    :return: List of tables
    """

    stmt = select(TableModel).offset(skip).limit(limit)
    result = db.execute(stmt).scalars().all()
    return result


def create_table(db: Session, table_in: TableCreate) -> TableModel:
    """
    Creates a new table.

    :param db: Session
    :param table_in: TableCreate
    :return: Table
    """

    try:
        db_table = TableModel(**table_in.model_dump(exclude_none=True))
        db.add(db_table)
        db.commit()
        db.refresh(db_table)
        return db_table
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании столика: {str(e)}",
        )


def delete_table(db: Session, table_id: int) -> Optional[TableModel]:
    """
    Deletes an existing table.

    :param db: Session
    :param table_id: ID of the table to delete
    :return: Table
    """

    try:
        db_table = get_table(db, table_id)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении столика: {str(e)}",
        )


def bulk_create_tables(
    db: Session, tables_data: List[Dict[str, Any]]
) -> List[TableModel]:
    """
    Creates multiple tables in bulk.

    :param db: Session
    :param tables_data: List of table data
    :return: List of created tables
    """
    try:
        tables = [TableModel(**data) for data in tables_data]
        db.add_all(tables)
        db.commit()
        for table in tables:
            db.refresh(table)
        return tables
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при массовом создании столиков: {str(e)}",
        )
