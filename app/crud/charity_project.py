from typing import Optional, List, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ) -> List[Dict[str, str]]:
        projects = await session.execute(
            select(CharityProject).where(CharityProject.fully_invested == 1)
        )
        projects = projects.scalars().all()
        project_list = []
        for project in projects:
            project_list.append({
                'name': project.name,
                'duration': project.close_date - project.create_date,
                'description': project.description
            })
        return sorted(project_list, key=lambda x: x['duration'])


charity_project_crud = CRUDCharityProject(CharityProject)
