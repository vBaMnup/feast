from typing import Dict, Any

from sqlalchemy.orm import Session

from src.tables.models import Table


def _create_table_object(db: Session, table_data: Dict[str, Any]) -> Table:
    """
    Вспомогательная функция для создания объекта столика

    Args:
        db: Сессия базы данных
        table_data: Данные столика

    Returns:
        Созданный объект столика
    """
    db_table = Table(**table_data)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table
