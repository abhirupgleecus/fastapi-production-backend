from fastapi import Depends, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    TokenResponseSchema,
    RegisterRequestSchema,
)
from app.services.auth_service import AuthService
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponseSchema
)
async def register(payload: RegisterRequestSchema, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user = await service.register_user(
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        company_id=payload.company_id,
    )

    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponseSchema(access_token=access_token)


@router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=TokenResponseSchema
)
async def login(
    payload_forn: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    access_token = await service.login_user(
        email=payload_forn.username, password=payload_forn.password
    )

    return TokenResponseSchema(access_token=access_token)
