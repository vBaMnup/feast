from typing import Dict, Any

from sqlalchemy.orm import Session

from src.tables.models import Table


def _create_table_object(db: Session, table_data: Dict[str, Any]) -> Table:
    """
    Create a table object in the database.

    Args:
        db: The database session.
        table_data: A dictionary containing the table data.

    Returns:
        The created table object.
    """

    db_table = Table(**table_data)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table
