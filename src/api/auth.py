from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select

from src.config import get_settings
from src.dependencies import AsyncDatabaseDep
from src.models.users import User as UserModel

##############################################################################################

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/token')
settings = get_settings()

##############################################################################################

def hash_password(password: str) -> str:
    """Преобразует пароль в хеш с использованием bcrypt."""

    return pwd_context.hash(password)

##############################################################################################

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли введённый пароль сохранённому хешу."""

    return pwd_context.verify(plain_password, hashed_password)

##############################################################################################

def create_access_token(data: dict) -> str:
    """Создаёт JWT с payload (sub, role, id, exp)."""

    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.api_access_token_expire_minutes)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.api_secret_key, algorithm=settings.api_jwt_encode_algorithm)

##############################################################################################

async def get_current_user(database: AsyncDatabaseDep, token: str = Depends(oauth2_scheme)):
    """Проверяет JWT и возвращает пользователя из базы."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token,
            settings.api_secret_key,
            algorithms=[settings.api_jwt_encode_algorithm],
        )
        email = payload.get('sub')
        if email is None:
            raise credentials_exception from None
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
            headers={'WWW-Authenticate': 'Bearer'},
        ) from None
    except jwt.PyJWTError:
        raise credentials_exception from None

    result = await database.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True))
    user = result.first()
    if user is None:
        raise credentials_exception from None

    return user

##############################################################################################
