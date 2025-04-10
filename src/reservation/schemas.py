from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TableBase(BaseModel):
    """Table schema."""

    name: str
    seats: int
    location: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TableCreate(TableBase):
    """Table creation schema."""

    pass


class Table(TableBase):
    """Table schema."""

    id: int


class ReservationBase(BaseModel):
    """Reservation schema."""

    customer_name: str
    table_id: int
    reservation_time: datetime
    duration_minutes: int

    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(ReservationBase):
    """Reservation creation schema."""

    pass


class Reservation(ReservationBase):
    """Reservation schema."""

    id: int
