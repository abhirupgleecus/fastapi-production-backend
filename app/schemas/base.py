from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime

class IDSchema(BaseSchema):
    id: UUID