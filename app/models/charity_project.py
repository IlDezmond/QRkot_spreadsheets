from datetime import datetime

from sqlalchemy import Column, event, String, Text

from .base import BaseModel


class CharityProject(BaseModel):
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)


@event.listens_for(CharityProject.fully_invested, 'set')
def update_close_date(target, value, oldvalue, initiator):
    if value and value != oldvalue:
        target.close_date = datetime.now()
        target.invested_amount = target.full_amount
