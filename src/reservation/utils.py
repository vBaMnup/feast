from sqlalchemy import select
from sqlalchemy.orm import Session

from src.reservation import models


def get_reservation_by_id(db: Session, reservation_id: int) -> models.Reservation:
    """
    Получение бронирования по его идентификатору

    Args:
        db: Сессия базы данных
        reservation_id: Идентификатор бронирования

    Returns:
        Объект бронирования или None, если бронирование не найдено
    """
    stmt = select(models.Reservation).where(models.Reservation.id == reservation_id)
    return db.scalar(stmt)
