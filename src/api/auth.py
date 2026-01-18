from collections.abc import Awaitable, Callable, Sequence
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from src.config import get_settings
from src.dependencies import AsyncDatabaseDep
from src.models import User as UserModel
from src.utils.routes import _validate_jwt_payload

##############################################################################################

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/token')
settings = get_settings()

##############################################################################################

def hash_password(password: str) -> str:
    """Преобразует пароль в хеш с использованием bcrypt."""

    return str(pwd_context.hash(password))

##############################################################################################

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли введённый пароль сохранённому хешу."""

    return bool(pwd_context.verify(plain_password, hashed_password))

##############################################################################################

def create_token(data: dict[str, str | int | datetime], access: bool) -> str:
    """Создаёт JWT с payload (sub, role, id, exp, type)."""

    to_encode = data.copy()
    time_delta = timedelta(minutes=settings.api_access_token_expire_minutes) if access else timedelta(days=settings.api_refresh_token_expire_days)
    token_type = 'access' if access else 'refresh'

    expire = datetime.now(UTC) + time_delta
    to_encode.update({'exp': expire, 'token_type': token_type})
    return jwt.encode(to_encode, settings.api_secret_key, algorithm=settings.api_jwt_encode_algorithm)

##############################################################################################

async def get_current_user(database: AsyncDatabaseDep, token: str = Depends(oauth2_scheme)) -> UserModel:
    """Проверяет JWT и возвращает пользователя из базы."""

    return await _validate_jwt_payload(
        token=token,
        secret_key=settings.api_secret_key,
        algorithm=settings.api_jwt_encode_algorithm,
        database=database,
    )

##############################################################################################

def is_authorized(permissions: Sequence[str]) -> Callable[[UserModel], Awaitable[UserModel]]:
    """Проверяет, что пользователь имеет соответствующую роль для выполнения операции."""

    async def _is_authorized(current_user: UserModel = Depends(get_current_user)) -> UserModel:
        if current_user.role in permissions:
            return current_user

        allowed_roles = ', '.join(permissions)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'Only [{allowed_roles}] allowed to prerform this action',
        )
    return _is_authorized

##############################################################################################
