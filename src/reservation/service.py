from datetime import timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.reservation import models, schemas
from src.tables.models import Table


def get_reservations(db: Session) -> List[models.Reservation]:
    """
    Get all reservations
    :param db: Session
    :return: List of reservations
    """

    return db.query(models.Reservation).all()


def create_reservation(
    db: Session, reservation: schemas.ReservationCreate
) -> models.Reservation:
    """
    Create reservation
    :param db: Session
    :param reservation: Reservation
    :return: Reservation
    """

    table = db.query(Table).filter(Table.id == reservation.table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table with id {reservation.table_id} not found",
        )

    end_time = reservation.reservation_time + timedelta(
        minutes=reservation.duration_minutes
    )

    conflicts = (
        db.query(models.Reservation)
        .filter(
            and_(
                models.Reservation.table_id == reservation.table_id,
                or_(
                    and_(
                        models.Reservation.reservation_time
                        <= reservation.reservation_time,
                        models.Reservation.reservation_time
                        + timedelta(minutes=models.Reservation.duration_minutes)
                        > reservation.reservation_time,
                    ),
                    and_(
                        models.Reservation.reservation_time < end_time,
                        models.Reservation.reservation_time
                        + timedelta(minutes=models.Reservation.duration_minutes)
                        >= end_time,
                    ),
                    and_(
                        models.Reservation.reservation_time
                        >= reservation.reservation_time,
                        models.Reservation.reservation_time
                        + timedelta(minutes=models.Reservation.duration_minutes)
                        <= end_time,
                    ),
                ),
            )
        )
        .first()
    )

    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table is already reserved during this time period",
        )

    db_reservation = models.Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def delete_reservation(db: Session, reservation_id: int) -> None:
    """
    Delete reservation
    :param db: Session
    :param reservation_id: Reservation
    :return: None
    """

    reservation = (
        db.query(models.Reservation)
        .filter(models.Reservation.id == reservation_id)
        .first()
    )
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with id {reservation_id} not found",
        )

    db.delete(reservation)
    db.commit()
    return None
