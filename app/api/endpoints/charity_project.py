from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_charity_project_closed, check_charity_project_exists,
    check_charity_project_invested, check_charity_project_invested_sum,
    check_name_duplicate
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models import Donation
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.investing import investing_process

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_charity_projects(
        session: AsyncSession = Depends(get_async_session),
):
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
):
    await check_name_duplicate(charity_project.name, session)
    new_project = await charity_project_crud.create(charity_project, session)
    await investing_process(new_project, Donation, session)
    return new_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
        project_id: int,
        obj_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    project = await check_charity_project_exists(project_id, session)
    check_charity_project_closed(project)
    if obj_in.name:
        await check_name_duplicate(obj_in.name, session)
    if obj_in.full_amount is not None:
        check_charity_project_invested_sum(project, obj_in.full_amount)

    charity_project = await charity_project_crud.update(
        project, obj_in, session
    )
    if charity_project.full_amount == charity_project.invested_amount:
        charity_project.fully_invested = True
        session.add(charity_project)
        await session.commit()
        await session.refresh(charity_project)

    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    project = await check_charity_project_exists(project_id, session)
    check_charity_project_invested(project)
    return await charity_project_crud.remove(
        project, session
    )
