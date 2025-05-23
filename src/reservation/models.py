from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
import datetime

from src.database import Base


class Reservation(Base):
    """Model for reservations."""

    __tablename__ = "reservations"

    __table_args__ = (
        Index("ix_table_id_reservation_time", "table_id", "reservation_time"),
    )

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    reservation_time = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.datetime.now(datetime.UTC),
    )
    duration_minutes = Column(Integer, nullable=False)

    table = relationship("Table", backref="reservations")

    def __repr__(self):
        return (
            f"<Reservation(id={self.id}, customer_name='{self.customer_name}', "
            f"table_id={self.table_id}, reservation_time={self.reservation_time}, "
            f"duration_minutes={self.duration_minutes})>"
        )
