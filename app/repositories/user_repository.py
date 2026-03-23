from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
            self, 
            email: str, 
            full_name: str,
            hashed_password: str,
            company_id: UUID
    ) -> User:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            company_id=company_id
        )
        self.db.add(user)
        await self.db.flush()
        return user
    
    async def update(
        self, 
        user: User, 
        email: str | None = None, 
        full_name: str | None = None,
        hashed_password: str | None = None
    ) -> User:
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if hashed_password is not None:
            user.hashed_password = hashed_password
        await self.db.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def list_by_company(self, company_id: UUID) -> Sequence[User]:
        result = await self.db.execute(
            select(User).where(User.company_id == company_id)
        )
        return result.scalars().all()
    
    async def delete(self, user: User) -> None:
        await self.db.delete(user)