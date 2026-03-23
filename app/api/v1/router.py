from app.api.v1.endpoints import users
from app.api.v1.endpoints import companies
from app.api.v1.endpoints import auth

from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(companies.router)
