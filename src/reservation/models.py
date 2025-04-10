from sqlalchemy import Column, Integer, String
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
