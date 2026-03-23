from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.api.dependencies import get_current_active_user
from app.db.models.user import User
from app.schemas.user import (
    UserCreateSchema,
    UserResponseSchema,
    UserUpdateSchema,
    UserListResponseSchema,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return UserResponseSchema.model_validate(current_user)


@router.get("/", response_model=UserListResponseSchema, status_code=status.HTTP_200_OK)
async def list_users(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db=db)
    users = await service.list_users(current_user=current_user)
    return UserListResponseSchema(
        users=[UserResponseSchema.model_validate(u) for u in users]
    )


@router.get(
    "/{user_id}", response_model=UserResponseSchema, status_code=status.HTTP_200_OK
)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)

    user = await service.get_user(current_user=current_user, user_id=user_id)

    return UserResponseSchema.model_validate(user)


@router.post(
    "/", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def create_user(
    payload: UserCreateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)

    user = await service.create_user(
        current_user=current_user,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
    )

    return UserResponseSchema.model_validate(user)


@router.patch(
    "/{user_id}", response_model=UserResponseSchema, status_code=status.HTTP_200_OK
)
async def update_user(
    user_id: UUID,
    payload: UserUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)

    user = await service.update_user(
        current_user=current_user,
        user_id=user_id,
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
    )

    return UserResponseSchema.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)

    await service.delete_user(current_user=current_user, user_id=user_id)

    return None
