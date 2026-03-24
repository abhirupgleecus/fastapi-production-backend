from uuid import UUID
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.company import Company
from app.repositories.company_repository import CompanyRepository
from app.repositories.user_repository import UserRepository

from app.core.exceptions import (
    NotFoundException,
    ConflictException,
)


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.company_repo = CompanyRepository(db)
        self.user_repo = UserRepository(db)

    # Create company

    async def create_company(
        self,
        *,
        name: str,
        description: str | None = None,
    ) -> Company:

        # Ensure name is unique
        existing_company = await self.company_repo.get_by_name(name)
        if existing_company is not None:
            raise ConflictException(f"Company with name {name} already exists.")

        company = await self.company_repo.create(name=name, description=description)
        await self.db.commit()
        await self.db.refresh(company)

        return company

    # Get company details

    async def get_company(
        self,
        *,
        company_id: UUID,
    ) -> Company:
        company = await self.company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundException(f"Company with id {company_id} not found.")
        return company

    # List companies

    async def list_companies(self) -> Sequence[Company]:
        return await self.company_repo.list()

    # Update company

    async def update_company(
        self,
        *,
        company_id: UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> Company:
        company = await self.company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundException(f"Company with id {company_id} not found.")

        # Ensure name is unique
        if name is not None:
            existing_company = await self.company_repo.get_by_name(name)
            if existing_company is not None and existing_company.id != company_id:
                raise ConflictException(f"Company with name {name} already exists.")

        updated_company = await self.company_repo.update(
            company, name=name, description=description
        )
        await self.db.commit()
        await self.db.refresh(updated_company)

        return updated_company

    # Delete company

    async def delete_company(
        self,
        *,
        company_id: UUID,
    ) -> None:
        company = await self.company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundException(f"Company with id {company_id} not found.")

        # Check if company has users
        users_in_company = await self.user_repo.list_by_company(company_id)

        if len(users_in_company) == 0:
            raise NotFoundException(
                f"Company with id {company_id} has no users. Cannot verify ownership."
            )

        if (
            len(users_in_company) > 1
        ):  # Ensures that only the last user is allowed to delete the company
            raise ConflictException("Delete all other users before deleting company.")

        last_user = users_in_company[0]

        # delete user first
        await self.user_repo.delete(last_user)

        # delete company after
        await self.company_repo.delete(company)

        await self.db.commit()
