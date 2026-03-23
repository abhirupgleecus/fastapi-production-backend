from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
)
from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    UnauthorizedException,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.company_repo = CompanyRepository(db)

    # Registration

    async def register_user(
        self,
        *,
        email: str,
        full_name: str,
        password: str,
        company_id: UUID,
    ) -> User:
        # Ensure company exists

        company = await self.company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundException(f"Company with id {company_id} not found.")

        # Ensure email is unique
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise ConflictException(f"User with email {email} already exists.")

        # Hash password
        hashed_password = hash_password(password)

        # Create user
        user = await self.user_repo.create(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            company_id=company_id,
        )

        await self.db.refresh(user)

        return user

    # Login

    async def login_user(
        self,
        *,
        email: str,
        password: str,
    ) -> str:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise UnauthorizedException("Invalid email or password.")

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive.")

        access_token = create_access_token(data={"sub": str(user.id)})
        return access_token
