from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.reservation.schemas import Reservation, ReservationCreate
from src.reservation.service import (
    get_reservations,
    create_reservation,
    delete_reservation,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get("/", response_model=List[Reservation])
def read_reservations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Read reservations

    Args:
        skip: The number of records to skip.
        limit: The maximum number of records to return.
        db: The database session.

    Returns:
        A list of reservations.
    """

    return get_reservations(db, skip, limit)


@router.post("/", response_model=Reservation, status_code=status.HTTP_201_CREATED)
def create_new_reservation(
    reservation_in: ReservationCreate, db: Session = Depends(get_db)
):
    """
    Create new reservation

    Args:
        reservation_in: The reservation data.
        db: The database session.

    Returns:
        The created reservation.
    """

    return create_reservation(db, reservation_in)


@router.delete("/{reservation_id}", response_model=Reservation)
def delete_existing_reservation(reservation_id: int, db: Session = Depends(get_db)):
    """
    Delete existing reservation

    Args:
        reservation_id: The ID of the reservation to delete.
        db: The database session.

    Returns:
        The deleted reservation.
    """

    result = delete_reservation(db, reservation_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Бронирование с id={reservation_id} не найдено."
        )
    return result
