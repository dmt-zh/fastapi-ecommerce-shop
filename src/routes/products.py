from collections.abc import Mapping, Sequence

from fastapi import APIRouter, status
from sqlalchemy import select, update

from src.dependencies import AsyncDatabaseDep
from src.models import Product as ProductModel
from src.routes.utils import _validate_parent_category, _validate_product_by_id
from src.schemas import Product as ProductSchema, ProductCreate

##############################################################################################

router = APIRouter(
    prefix='/products',
    tags=['products'],
)

##############################################################################################

@router.get(
    path='/',
    response_model=Sequence[ProductSchema],
)
async def get_all_products(database: AsyncDatabaseDep) -> Sequence[ProductSchema] | list:
    """Возвращает список всех товаров."""

    sql_query = select(ProductModel).where(ProductModel.is_active == True)
    products = await database.scalars(sql_query)
    return products.all()

##############################################################################################

@router.post(
    path='/',
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product: ProductCreate,
    database: AsyncDatabaseDep,
) -> ProductSchema:
    """Создаёт новый товар."""

    await _validate_parent_category(product.category_id, database)
    new_product = ProductModel(**product.model_dump())
    database.add(new_product)
    await database.commit()

    return new_product

##############################################################################################

@router.get(
    path='/category/{category_id}',
    response_model=Sequence[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int,
    database: AsyncDatabaseDep,
) -> Sequence[ProductSchema] | list:
    """Возвращает список товаров в указанной категории по её ID."""

    await _validate_parent_category(category_id, database)
    sql_query = select(ProductModel).where(
        ProductModel.category_id == category_id,
        ProductModel.is_active == True,
    )
    products = await database.scalars(sql_query)

    return products.all()

##############################################################################################

@router.get(
    path='/{product_id}',
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: int, database: AsyncDatabaseDep) -> ProductSchema:
    """Возвращает детальную информацию о товаре по его ID."""

    product = await _validate_product_by_id(product_id, database)
    await _validate_parent_category(product.category_id, database)

    return product

##############################################################################################

@router.put(
    path='/{product_id}',
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: int,
    product: ProductCreate,
    database: AsyncDatabaseDep,
) -> ProductSchema:
    """Обновляет товар по его ID."""

    product_to_update = await _validate_product_by_id(product_id, database)
    await _validate_parent_category(product_to_update.category_id, database)

    await database.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump()),
    )
    await database.commit()

    return product_to_update

##############################################################################################

@router.delete(
    path='/{product_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_product(product_id: int, database: AsyncDatabaseDep) -> Mapping[str, str]:
    """Удаляет товар по его ID."""

    await _validate_product_by_id(product_id, database)
    await database.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(is_active=False),
    )
    await database.commit()

    return {'status': 'success', 'message': 'Product marked as inactive'}

##############################################################################################
