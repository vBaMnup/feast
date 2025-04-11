from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.reservation import models, schemas
from src.reservation.exceptions import (
    validate_reservation_data,
    validate_table_exists,
    check_reservation_conflicts,
)
from src.reservation.utils import get_reservation_by_id


def get_reservations(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Reservation]:
    """
    Получение списка всех бронирований с пагинацией

    Args:
        db: Сессия базы данных
        skip: Количество пропускаемых записей
        limit: Максимальное количество возвращаемых записей

    Returns:
        Список объектов бронирования
    """
    stmt = select(models.Reservation).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create_reservation(
    db: Session, reservation_in: schemas.ReservationCreate
) -> models.Reservation:
    """
    Создание нового бронирования с проверкой доступности стола

    Args:
        db: Сессия базы данных
        reservation_in: Данные нового бронирования

    Returns:
        Созданный объект бронирования

    Raises:
        HTTPException: При невалидных входных данных или конфликте бронирования
    """
    # Проверка существования стола
    validate_table_exists(db, reservation_in.table_id)

    # Валидация данных бронирования
    validate_reservation_data(reservation_in)

    try:
        # Проверка на конфликты бронирования
        check_reservation_conflicts(db, reservation_in)

        # Создание бронирования
        reservation = models.Reservation(
            customer_name=reservation_in.customer_name,
            table_id=reservation_in.table_id,
            reservation_time=reservation_in.reservation_time,
            duration_minutes=reservation_in.duration_minutes,
        )

        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания бронирования: {str(e)}",
        )


def delete_reservation(db: Session, reservation_id: int) -> None:
    """
    Удаление существующего бронирования

    Args:
        db: Сессия базы данных
        reservation_id: Идентификатор удаляемого бронирования

    Raises:
        HTTPException: Если бронирование не найдено или возникла ошибка при удалении
    """
    try:
        reservation = get_reservation_by_id(db, reservation_id)

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Бронирование с id {reservation_id} не найдено",
            )

        db.delete(reservation)
        db.commit()

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка удаления бронирования: {str(e)}",
        )
