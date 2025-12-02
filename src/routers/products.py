from collections.abc import Mapping, Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.models import Product as ProductModel
from src.routers.utils import _validate_parent_category, _validate_product_by_id
from src.schemas import Product as ProductSchema, ProductCreate
from src.dependencies import SyncDatabaseDep

##############################################################################################

products_router = APIRouter(
    prefix='/products',
    tags=['products'],
)

##############################################################################################

@products_router.get(
    path='/',
    response_model=Sequence[ProductSchema],
)
async def get_all_products(database: SyncDatabaseDep) -> Sequence[ProductSchema] | list:
    """Возвращает список всех товаров."""

    sql_query = select(ProductModel).where(ProductModel.is_active == True)
    return database.scalars(sql_query).all()

##############################################################################################

@products_router.post(
    path='/',
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product: ProductCreate,
    database: SyncDatabaseDep,
) -> ProductSchema:
    """Создаёт новый товар."""

    _validate_parent_category(product.category_id, database)
    new_product = ProductModel(**product.model_dump())
    database.add(new_product)
    database.commit()
    database.refresh(new_product)

    return new_product

##############################################################################################

@products_router.get(
    path='/category/{category_id}',
    response_model=Sequence[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int,
    database: SyncDatabaseDep,
) -> Sequence[ProductSchema] | list:
    """Возвращает список товаров в указанной категории по её ID."""

    _validate_parent_category(category_id, database)
    sql_query = select(ProductModel).where(
        ProductModel.category_id == category_id,
        ProductModel.is_active == True,
    )

    return database.scalars(sql_query).all()

##############################################################################################

@products_router.get(
    path='/{product_id}',
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: int, database: SyncDatabaseDep) -> ProductSchema:
    """Возвращает детальную информацию о товаре по его ID."""

    product = _validate_product_by_id(product_id, database)
    _validate_parent_category(product.category_id, database)

    return product

##############################################################################################

@products_router.put(
    path='/{product_id}',
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: int,
    product: ProductCreate,
    database: SyncDatabaseDep,
) -> ProductSchema:
    """Обновляет товар по его ID."""

    product_to_update = _validate_product_by_id(product_id, database)
    _validate_parent_category(product_to_update.category_id, database)

    database.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump()),
    )
    database.commit()
    database.refresh(product_to_update)

    return product_to_update

##############################################################################################

@products_router.delete(
    path='/{product_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_product(product_id: int, database: SyncDatabaseDep) -> Mapping[str, str]:
    """Удаляет товар по его ID."""

    _validate_product_by_id(product_id, database)
    database.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(is_active=False),
    )
    database.commit()

    return {'status': 'success', 'message': 'Product marked as inactive'}

##############################################################################################
