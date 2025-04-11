from datetime import timedelta, datetime

from fastapi import HTTPException, status
from sqlalchemy import exists, and_, func
from sqlalchemy.orm import Session

from src.reservation import models, schemas
from src.tables.models import Table


def validate_table_exists(db: Session, table_id: int) -> None:
    """
    Проверка существования стола с указанным ID

    Args:
        db: Сессия базы данных
        table_id: Идентификатор проверяемого стола

    Raises:
        HTTPException: Если стол не найден
    """
    table = db.get(Table, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Стол с ID {table_id} не найден.",
        )


def validate_reservation_data(reservation_data: schemas.ReservationCreate) -> None:
    """
    Валидация данных бронирования

    Args:
        reservation_data: Данные для проверки

    Raises:
        HTTPException: При обнаружении невалидных данных
    """
    if reservation_data.duration_minutes <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Продолжительность бронирования должна быть больше нуля.",
        )

    if reservation_data.reservation_time < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время бронирования не может быть в прошлом.",
        )


def check_reservation_conflicts(
    db: Session, reservation_data: schemas.ReservationCreate
) -> None:
    """
    Проверка на конфликты с существующими бронированиями

    Args:
        db: Сессия базы данных
        reservation_data: Данные проверяемого бронирования

    Raises:
        HTTPException: При обнаружении конфликта бронирования
    """
    new_start = reservation_data.reservation_time
    new_end = new_start + timedelta(minutes=reservation_data.duration_minutes)

    conflict_subquery = (
        exists()
        .where(
            and_(
                models.Reservation.table_id == reservation_data.table_id,
                models.Reservation.reservation_time < new_end,
                (
                    models.Reservation.reservation_time
                    + func.make_interval(
                        0, 0, 0, 0, 0, models.Reservation.duration_minutes
                    )
                )
                > new_start,
            )
        )
        .select()
    )

    if db.scalar(conflict_subquery):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Конфликт бронирования: столик уже занят в указанный временной слот.",
        )
