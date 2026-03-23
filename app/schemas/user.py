from pydantic import EmailStr, Field
from uuid import UUID
from typing import List, Optional

from app.schemas.base import BaseSchema, TimestampSchema, IDSchema

#User create
class UserCreateSchema(BaseSchema):
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6)

#User update
class UserUpdateSchema(BaseSchema):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    password: Optional[str] = Field(None, min_length=6)

#User Response
class UserResponseSchema(IDSchema, TimestampSchema):
    email: str
    full_name: str
    is_active: bool
    company_id: UUID

#User list response
class UserListResponseSchema(BaseSchema):
    users: List[UserResponseSchema]