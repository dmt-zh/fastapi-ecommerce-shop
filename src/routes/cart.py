from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from src.api.auth import is_authorized
from src.dependencies import AsyncDatabaseDep
from src.models.catr import CartItem as CartItemModel
from src.models.users import User as UserModel
from src.schemas import Cart as CartSchema, CartItem as CartItemSchema, CartItemCreate, CartItemUpdate
from src.utils.routes import _get_cart_item, _validate_parent_category, _validate_product_by_id

router = APIRouter(prefix='/cart', tags=['cart'])


@router.get(
    path='/',
    response_model=CartSchema,
)
async def get_cart(
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('seller', 'buyer'))),
) -> CartSchema:
    """Получение данных корзины пользователя."""
    result = await database.scalars(
        select(CartItemModel)
        .options(selectinload(CartItemModel.product))
        .where(CartItemModel.user_id == current_user.id)
        .order_by(CartItemModel.id),
    )
    items: list[CartItemSchema] = result.all()  # type: ignore[assignment]
    total_quantity = sum(item.quantity for item in items)
    price_items = (
        Decimal(item.quantity) *
        (item.product.price if item.product.price is not None else Decimal('0'))
        for item in items
    )
    total_price_decimal = sum(price_items, Decimal('0'))

    return CartSchema(
        user_id=current_user.id,
        items=items,
        total_quantity=total_quantity,
        total_price=total_price_decimal,
    )


@router.post(
    path='/items',
    response_model=CartItemSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_item_to_cart(
    payload: CartItemCreate,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('seller', 'buyer'))),
) -> CartItemModel | None:
    """Добавление товара в корзину."""
    product = await _validate_product_by_id(payload.product_id, database)
    await _validate_parent_category(product.category_id, database)

    cart_item = await _get_cart_item(database, current_user.id, payload.product_id)
    if cart_item:
        cart_item.quantity += payload.quantity
    else:
        cart_item = CartItemModel(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        database.add(cart_item)

    await database.commit()
    return await _get_cart_item(database, current_user.id, payload.product_id)


@router.put(
    path='/items/{product_id}',
    response_model=CartItemSchema,
    status_code=status.HTTP_200_OK,
)
async def update_cart_item(
    product_id: int,
    payload: CartItemUpdate,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('seller', 'buyer'))),
) -> CartItemModel | None:
    """Обновление количества товаров в корзине."""
    product = await _validate_product_by_id(product_id, database)
    await _validate_parent_category(product.category_id, database)

    cart_item = await _get_cart_item(database, current_user.id, product_id)
    if cart_item is None:
        raise HTTPException(status_code=404, detail='Cart item not found')

    cart_item.quantity = payload.quantity
    await database.commit()
    return await _get_cart_item(database, current_user.id, product_id)


@router.delete(
    path='/items/{product_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_item_from_cart(
    product_id: int,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('seller', 'buyer'))),
) -> Response:
    """Удаление товара из корзины."""
    cart_item = await _get_cart_item(database, current_user.id, product_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail='Cart item not found')

    await database.delete(cart_item)
    await database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path='/',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_cart(
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('seller', 'buyer'))),
) -> Response:
    """Полная очистка корзины."""
    await database.execute(delete(CartItemModel).where(CartItemModel.user_id == current_user.id))
    await database.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
