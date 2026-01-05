from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.models.users import User as UserModel
from src.schemas.users import UserCreate, User as UserSchema
from src.dependencies import AsyncDatabaseDep
from src.api.auth import hash_password

##############################################################################################

router = APIRouter(prefix='/users', tags=['users'])

##############################################################################################

@router.post(
    path='/',
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_user(user: UserCreate, database: AsyncDatabaseDep) -> UserSchema:
    """Регистрирует нового пользователя с ролью 'buyer' или 'seller'."""

    result = await database.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')

    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
    )

    database.add(db_user)
    await database.commit()
    return db_user

##############################################################################################
