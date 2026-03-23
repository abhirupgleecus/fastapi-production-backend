from passlib.context import CryptContext

from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from app.core.config import get_settings

from jose import jwt

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=get_settings().JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, get_settings().JWT_SECRET_KEY, algorithm=get_settings().JWT_ALGORITHM
    )
    return encoded_jwt


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
