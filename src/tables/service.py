from typing import List, Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.tables.models import Table as TableModel
from src.tables.schemas import TableCreate
from src.tables.exceptions import create_db_error
from src.tables.utils import _create_table_object


def get_tables(db: Session, skip: int = 0, limit: int = 100) -> List[TableModel]:
    """
    Получение списка столиков с пагинацией

    Args:
        db: Сессия базы данных
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей

    Returns:
        Список объектов столиков
    """
    stmt = select(TableModel).offset(skip).limit(limit)
    return db.execute(stmt).scalars().all()


def create_table(db: Session, table_in: TableCreate) -> TableModel:
    """
    Создание нового столика

    Args:
        db: Сессия базы данных
        table_in: Данные для создания столика

    Returns:
        Созданный объект столика

    Raises:
        HTTPException: При ошибке создания столика
    """
    try:
        return _create_table_object(db, table_in.model_dump(exclude_none=True))
    except SQLAlchemyError as e:
        db.rollback()
        raise create_db_error("создании", str(e))


def delete_table(db: Session, table_id: int) -> Optional[TableModel]:
    """
    Удаление существующего столика

    Args:
        db: Сессия базы данных
        table_id: Идентификатор удаляемого столика

    Returns:
        Удаленный объект столика

    Raises:
        HTTPException: Если столик не найден или возникла ошибка при удалении
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
