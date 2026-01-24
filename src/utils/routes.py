import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.sql import Select, func

from src.dependencies import AsyncDatabaseDep
from src.models import Category as CategoryModel, Product as ProductModel, Review as ReviewModel
from src.models.users import User as UserModel
from src.schemas import CategoryCreate


def _build_category_query(category: CategoryCreate | int) -> Select[tuple[CategoryModel]]:
    """Формируется базовый запрос для извлечения категорий."""
    category_id = category if isinstance(category, int) else category.parent_id
    return select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True,
    )


async def _validate_parent_category(category: CategoryCreate | int, database: AsyncDatabaseDep) -> None:
    """Проверяется наличие родительской категории."""
    if isinstance(category, CategoryCreate) and category.parent_id is None:
        return

    sql_query = _build_category_query(category)
    categories = await database.scalars(sql_query)
    parent_category = categories.first()
    if parent_category is None:
        raise HTTPException(status_code=400, detail='Parent category not found')


async def _validate_product_by_id(product_id: int, database: AsyncDatabaseDep) -> ProductModel:
    """Проверяется наличие товара по указанному идентификатору."""
    sql_query = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True,
    )
    products = await database.scalars(sql_query)
    product_item = products.first()
    if product_item is None:
        raise HTTPException(status_code=404, detail='Product not found')
    return product_item


async def _update_product_rating(product_id: int, database: AsyncDatabaseDep) -> None:
    """Пересчёт рейтинга товара при добавлении отзыва."""
    result = await database.execute(
        select(func.avg(ReviewModel.grade)).where(
            ReviewModel.product_id == product_id,
            ReviewModel.is_active == True,
        ),
    )
    avg_rating = result.scalar() or 0.0
    product = await database.get(ProductModel, product_id)
    if product is not None:
        product.rating = avg_rating
        await database.commit()


class CredentialsException(HTTPException):
    """CredentialsException.

    Исключение для ошибок аутентификации (HTTP 401 Unauthorized).

    Используется, когда не удается проверить учетные данные, токен истек
    или имеет неверный формат. Автоматически добавляет необходимый заголовок
    'WWW-Authenticate: Bearer' согласно спецификации OAuth2.

    Args:
        detail (str): Описание ошибки, которое будет отправлено клиенту.
    """

    def __init__(self, detail: str = 'Could not validate credentials') -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={'WWW-Authenticate': 'Bearer'},
        )


async def _validate_jwt_payload(
    token: str,
    secret_key: str,
    algorithm: str,
    database: AsyncDatabaseDep,
    type_check: bool = False,
) -> UserModel:
    """Проверяет валидность JWT-токена и наличие активного пользователя в базе данных."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email = payload.get('sub')
        token_condition = payload.get('token_type').startswith('refresh') if type_check else True

        if email is None or not token_condition:
            raise CredentialsException(detail='Could not validate token: email or token_type is invalid') from None
    except jwt.ExpiredSignatureError:
        raise CredentialsException(detail='Could not validate token: it has expired') from None
    except jwt.PyJWTError:
        raise CredentialsException(detail='Could not validate token: payload decoding error') from None

    user = await database.scalar(
        select(UserModel).where(
            UserModel.email == email,
            UserModel.is_active == True,
        ),
    )
    if user is None:
        raise CredentialsException(detail='Could not validate token: inactive user')
    return user
