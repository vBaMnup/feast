from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TableBase(BaseModel):
    """Table schema."""

    name: str
    seats: int = Field(gt=0)
    location: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TableCreate(TableBase):
    """Table creation schema."""

    pass


class Table(TableBase):
    """Table schema."""

    id: int
