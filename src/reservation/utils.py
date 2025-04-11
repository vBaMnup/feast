from sqlalchemy import select
from sqlalchemy.orm import Session

from src.reservation import models


def get_reservation_by_id(db: Session, reservation_id: int) -> models.Reservation:
    """
    Get a reservation by its ID.

    Args:
        db: The database session.
        reservation_id: The ID of the reservation to retrieve.

    Returns:
        The reservation object.
    """

    stmt = select(models.Reservation).where(models.Reservation.id == reservation_id)
    return db.scalar(stmt)
