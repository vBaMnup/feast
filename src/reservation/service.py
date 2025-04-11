from datetime import timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select, exists, and_, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.reservation import models, schemas


def get_reservations(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.Reservation]:
    """
    Gets all reservations
    :param db: Session
    :param skip: Skips
    :param limit: Limit
    :return: List
    """

    stmt = select(models.Reservation).offset(skip).limit(limit)
    return db.scalars(stmt).all()


def create_reservation(
    db: Session, reservation_in: schemas.ReservationCreate
) -> models.Reservation:
    """
    Creates a new reservation
    :param db: Session
    :param reservation_in: Reservation
    :return: Reservation
    """

    try:
        new_start = reservation_in.reservation_time
        new_end = new_start + timedelta(minutes=reservation_in.duration_minutes)

        conflict_subquery = (
            exists()
            .where(
                and_(
                    models.Reservation.table_id == reservation_in.table_id,
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

        db_reservation = models.Reservation(
            **reservation_in.model_dump(exclude_none=True)
        )
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        return db_reservation

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании бронирования: {str(e)}",
        )


def delete_reservation(db: Session, reservation_id: int) -> None:
    """
    Deletes a reservation
    :param db: Session
    :param reservation_id: Reservation
    :return: None
    """

    stmt = select(models.Reservation).where(models.Reservation.id == reservation_id)
    reservation = db.scalar(stmt)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с id {reservation_id} не найдено",
        )

    db.delete(reservation)
    db.commit()
