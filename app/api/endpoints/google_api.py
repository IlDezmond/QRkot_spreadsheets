from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.google_api import make_spreadsheet

router = APIRouter()


@router.get(
    '/',
    dependencies=[Depends(current_superuser)]
)
async def get_report(
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service),
):
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )
    background_tasks.add_task(make_spreadsheet, wrapper_services, projects)
    return projects
