from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.company import Company


class CompanyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, name: str, description: str | None = None) -> Company:
        company = Company(name=name, description=description)
        self.db.add(company)
        await self.db.flush()
        return company

    async def get_by_id(self, company_id: UUID) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Company | None:
        result = await self.db.execute(select(Company).where(Company.name == name))
        return result.scalar_one_or_none()

    async def list(self) -> Sequence[Company]:
        result = await self.db.execute(select(Company))
        return result.scalars().all()

    async def update(
        self,
        company: Company,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> Company:

        if name is not None:
            company.name = name
        if description is not None:
            company.description = description

        await self.db.flush()
        return company

    async def delete(self, company: Company) -> None:
        await self.db.delete(company)
