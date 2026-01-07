from collections.abc import Mapping

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from src.api.auth import create_access_token, hash_password, verify_password
from src.dependencies import AsyncDatabaseDep, OAuth2PasswordRequestFormDep
from src.models.users import User as UserModel
from src.schemas.users import User as UserSchema, UserCreate

##############################################################################################

router = APIRouter(prefix='/users', tags=['users'])

##############################################################################################

@router.post(
    path='/',
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(user: UserCreate, database: AsyncDatabaseDep) -> UserSchema:
    """Регистрирует нового пользователя с ролью 'buyer' или 'seller'."""

    result = await database.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')

    new_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
    )

    database.add(new_user)
    await database.commit()
    return new_user

##############################################################################################

@router.post(path='/token')
async def login(form_data: OAuth2PasswordRequestFormDep, database: AsyncDatabaseDep) -> Mapping[str, str]:
    """Аутентифицирует пользователя и возвращает JWT с email, role и id."""

    user = await database.scalar(
        select(UserModel).where(
            UserModel.email == form_data.username,
            UserModel.is_active == True,
        ),
    )
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(data={'sub': user.email, 'role': user.role, 'id': user.id})
    return {'access_token': access_token, 'token_type': 'bearer'}

##############################################################################################
