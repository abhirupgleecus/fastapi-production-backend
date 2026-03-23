from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

#import models for alembic autogenerate
from app.db.models import user, company