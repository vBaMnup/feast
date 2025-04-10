import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base


class Table(Base):
    """Model for tables."""

    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    seats = Column(Integer, nullable=False)
    location = Column(String, nullable=False)

    def __repr__(self):
        return f"<Table(id={self.id}, name='{self.name}', seats={self.seats}, location='{self.location}')>"


class Reservation(Base):
    """Model for reservations."""

    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    reservation_time = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    duration_minutes = Column(Integer, nullable=False)

    table = relationship("Table", backref="reservations")

    def __repr__(self):
        return (
            f"<Reservation(id={self.id}, customer_name='{self.customer_name}', "
            f"table_id={self.table_id}, reservation_time={self.reservation_time}, "
            f"duration_minutes={self.duration_minutes})>"
        )
