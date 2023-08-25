from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

from app.core.config import settings


class CharityProjectBase(BaseModel):
    name: str = Field(
        ...,
        min_length=settings.min_str_length,
        max_length=settings.max_str_length
    )
    description: str = Field(..., min_length=settings.min_str_length)
    full_amount: PositiveInt

    class Config:
        extra = Extra.forbid


class CharityProjectDB(CharityProjectBase):
    id: int
    create_date: datetime
    close_date: Optional[datetime]
    invested_amount: int = Field(0)
    fully_invested: bool = Field(False)

    class Config:
        orm_mode = True


class CharityProjectCreate(CharityProjectBase):
    pass

    class Config:
        min_anystr_length = settings.min_str_length


class CharityProjectUpdate(CharityProjectCreate):
    name: Optional[str] = Field(
        None,
        min_length=settings.min_str_length,
        max_length=settings.max_str_length
    )
    description: Optional[str] = Field(
        None,
        min_length=settings.min_str_length
    )
    full_amount: Optional[PositiveInt] = Field(None)
