from datetime import timedelta, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import exists, and_, func
from sqlalchemy.orm import Session

from src.reservation import models, schemas
from src.tables.models import Table


def validate_table_exists(db: Session, table_id: int) -> None:
    """
    Checks if a table with the given ID exists in the database.

    Args:
        db: The database session.
        table_id: The ID of the table to check.

    Raises:
        HTTPException: If the table is not found.
    """

    table = db.get(Table, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Стол с ID {table_id} не найден.",
        )


def validate_reservation_data(reservation_data: schemas.ReservationCreate) -> None:
    """
    Checks if the reservation data is valid.

    Args:
        reservation_data: The reservation data to validate.

    Raises:
        HTTPException: If the reservation data is not valid.
    """

    if reservation_data.duration_minutes <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Продолжительность бронирования должна быть больше нуля.",
        )

    if reservation_data.reservation_time < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Время бронирования не может быть в прошлом.",
        )


def check_reservation_conflicts(
    db: Session, reservation_data: schemas.ReservationCreate
) -> None:
    """
    Checks for conflicts between existing reservations and the new reservation.

    Args:
        db: The database session.
        reservation_data: The new reservation data.

    Raises:
        HTTPException: If a conflict is found.
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
