from typing import Type, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def get_not_full_invested_objects(
        model: Type[Union[CharityProject, Donation]],
        session: AsyncSession
):
    objects = await session.execute(
        select(model).where(model.fully_invested == 0).
        order_by(model.create_date)
    )
    return objects.scalars().all()


def invest(
        obj_in: Union[CharityProject, Donation],
        obj_model: Union[CharityProject, Donation],
):
    free_amount_in = obj_in.full_amount - obj_in.invested_amount
    free_amount_model = obj_model.full_amount - obj_model.invested_amount

    if free_amount_in > free_amount_model:
        obj_in.invested_amount += free_amount_model
        obj_model.fully_invested = True
    elif free_amount_in < free_amount_model:
        obj_model.invested_amount += free_amount_in
        obj_in.fully_invested = True
    else:
        obj_in.fully_invested = True
        obj_model.fully_invested = True

    return obj_in, obj_model


async def investing_process(
        obj_in: Union[CharityProject, Donation],
        model_add: Type[Union[CharityProject, Donation]],
        session: AsyncSession,
):
    model_objects = await get_not_full_invested_objects(model_add, session)

    for obj in model_objects:
        obj_in, obj = invest(obj_in, obj)
        session.add(obj_in)
        session.add(obj)
        if obj_in.fully_invested:
            break

    await session.commit()
    await session.refresh(obj_in)
    return obj_in
