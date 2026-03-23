from pydantic import EmailStr, Field
from uuid import UUID

from app.schemas.base import BaseSchema


class RegisterRequestSchema(BaseSchema):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=1, max_length=255)
    company_id: UUID


class LoginRequestSchema(BaseSchema):
    email: EmailStr
    password: str


class TokenResponseSchema(BaseSchema):
    access_token: str
    token_type: str = "bearer"
