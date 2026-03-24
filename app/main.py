from fastapi import FastAPI
from app.api.v1.router import api_router
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.core.exceptions import (
    NotFoundException,
    ConflictException,
    ForbiddenException,
    UnauthorizedException,
)


app = FastAPI()

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(NotFoundException)
async def not_found_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(ConflictException)
async def conflict_handler(request: Request, exc: ConflictException):
    return JSONResponse(
        status_code=409,
        content={"detail": str(exc)},
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=401,
        content={"detail": str(exc)},
    )


@app.exception_handler(ForbiddenException)
async def forbidden_handler(request: Request, exc: ForbiddenException):
    return JSONResponse(
        status_code=403,
        content={"detail": str(exc)},
    )
