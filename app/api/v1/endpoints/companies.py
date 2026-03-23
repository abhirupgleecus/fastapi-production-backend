from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_active_user
from app.db.models.user import User

from app.schemas.company import(
    CompanyCreateSchema,
    CompanyUpdateSchema,
    CompanyResponseSchema,
)

from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies",tags=["companies"])

#Create company(public route)
@router.post("/", response_model=CompanyResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: CompanyCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    company = await service.create_company(
        name=payload.name,
        description=payload.description,
    )

    return CompanyResponseSchema.model_validate(company)

#Get company
@router.get("/my_company", response_model=CompanyResponseSchema, status_code=status.HTTP_200_OK)
async def get_company(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    service = CompanyService(db)

    company = await service.get_company(
        company_id=current_user.company_id
    )

    return CompanyResponseSchema.model_validate(company)

#Update company
@router.put("/update_my_company", response_model=CompanyResponseSchema, status_code=status.HTTP_200_OK)
async def update_company(
    payload: CompanyUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    service = CompanyService(db)

    company = await service.update_company(
        company_id=current_user.company_id,
        name=payload.name,
        description=payload.description,
    )

    return CompanyResponseSchema.model_validate(company)

#Delete company
@router.delete("/delete_my_company", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    service = CompanyService(db)

    await service.delete_company(
        company_id=current_user.company_id
    )

    return None