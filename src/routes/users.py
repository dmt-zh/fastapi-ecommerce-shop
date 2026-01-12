import jwt
from collections.abc import Mapping
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from src.api.auth import create_token, hash_password, verify_password
from src.dependencies import AsyncDatabaseDep, OAuth2PasswordRequestFormDep, SettingsDep
from src.models.users import User as UserModel
from src.utils.routes import CredentialsException, _validate_jwt_payload
from src.schemas.users import User as UserSchema, UserCreate, RefreshTokenRequest

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
        raise CredentialsException(detail='Incorrect email or password')
    
    access_token = create_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id},
        access=True,
    )
    refresh_token = create_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id},
        access=False,
    )
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}

##############################################################################################

@router.post(path='/refresh-token')
async def refresh_token(
    body: RefreshTokenRequest,
    database: AsyncDatabaseDep,
    settings: SettingsDep,
) -> Mapping[str, str]:
    """Обновляет refresh-токен, принимая старый refresh-токен в теле запроса."""

    user = await _validate_jwt_payload(
        token=body.refresh_token,
        secret_key=settings.api_secret_key,
        algorithm=settings.api_jwt_encode_algorithm,
        database=database,
        type_check=True,
    )
    new_refresh_token = create_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id},
        access=False,
    )

    return {'refresh_token': new_refresh_token, 'token_type': 'bearer'}

##############################################################################################

@router.post(path='/access-token')
async def access_token(
    body: RefreshTokenRequest,
    database: AsyncDatabaseDep,
    settings: SettingsDep,
) -> Mapping[str, str]:
    """Обновляет refresh-токен, принимая старый refresh-токен в теле запроса."""

    user = await _validate_jwt_payload(
        token=body.refresh_token,
        secret_key=settings.api_secret_key,
        algorithm=settings.api_jwt_encode_algorithm,
        database=database,
        type_check=True,
    )
    new_access_token = create_token(
        data={'sub': user.email, 'role': user.role, 'id': user.id},
        access=True,
    )

    return {'access_token': new_access_token, 'token_type': 'bearer'}

##############################################################################################
