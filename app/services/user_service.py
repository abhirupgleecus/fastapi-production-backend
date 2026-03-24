from uuid import UUID
from typing import Sequence, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.core.security import hash_password
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    ForbiddenException,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.company_repo = CompanyRepository(db)

    # Internal helpers

    async def _ensure_same_company(
        self,
        *,
        current_user: User,
        target_user: User,
    ) -> None:
        if current_user.company_id != target_user.company_id:
            raise ForbiddenException(
                "You do not have permission to access this resource."
            )

    async def _ensure_email_unique(
        self,
        email: str,
    ) -> None:
        existing_user_email = await self.user_repo.get_by_email(email)
        if existing_user_email is not None:
            raise ConflictException(f"User with email {email} already exists.")

    # Public methods

    async def create_user(
        self,
        *,
        current_user: User,
        email: str,
        full_name: str,
        password: str,
    ) -> User:
        # Multitenant check
        company_id = current_user.company_id

        await self._ensure_email_unique(email)

        hashed_password = hash_password(password)

        user = await self.user_repo.create(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            company_id=company_id,
        )
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_user(
        self,
        *,
        current_user: User,
        user_id: UUID,
    ) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")

        await self._ensure_same_company(current_user=current_user, target_user=user)

        return user

    async def list_users(
        self,
        *,
        current_user: User,
    ) -> Sequence[User]:
        users_by_company = await self.user_repo.list_by_company(current_user.company_id)
        return users_by_company

    async def update_user(
        self,
        *,
        current_user: User,
        user_id: UUID,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")
        await self._ensure_same_company(current_user=current_user, target_user=user)
        if email is not None and email != user.email:
            await self._ensure_email_unique(email)

        hashed_password = None
        if password is not None:
            hashed_password = hash_password(password)

        updated_user = await self.user_repo.update(
            user=user,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
        )
        await self.db.commit()
        await self.db.refresh(updated_user)

        return updated_user

    async def delete_user(
        self,
        *,
        current_user: User,
        user_id: UUID,
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found.")
        await self._ensure_same_company(current_user=current_user, target_user=user)
        await self.user_repo.delete(user)
        await self.db.commit()
