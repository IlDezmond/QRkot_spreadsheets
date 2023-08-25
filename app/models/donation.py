from datetime import datetime

from sqlalchemy import Column, event, ForeignKey, Integer, Text

from .base import BaseModel


class Donation(BaseModel):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)


@event.listens_for(Donation.fully_invested, 'set')
def update_close_date(target, value, oldvalue, initiator):
    if value and value != oldvalue:
        target.close_date = datetime.now()
        target.invested_amount = target.full_amount
