from pydantic import Field
from typing import List, Optional

from app.schemas.base import BaseSchema, TimestampSchema, IDSchema

#Company create
class CompanyCreateSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

#Company Update
class CompanyUpdateSchema(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None

#Company Response
class CompanyResponseSchema(IDSchema, TimestampSchema):
    name: str
    description: str | None
    