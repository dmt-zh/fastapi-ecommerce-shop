from collections.abc import Mapping, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select
from src.models import Product as ProductModel
from src.schemas import Product as ProductSchema, ProductCreate, CategoryCreate
from src.services import get_db
from src.routers.utils import _validate_parent_category, _validate_product_by_id


products_router = APIRouter(
    prefix='/products',
    tags=['products'],
)

##############################################################################################

@products_router.get(
    path='/',
    response_model=Sequence[ProductSchema],
)
async def get_all_products(database: Session = Depends(get_db)) -> Sequence[ProductSchema] | list:
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
    database: Session = Depends(get_db),
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
    database: Session = Depends(get_db)
) -> Sequence[ProductSchema] | list:
    """Возвращает список товаров в указанной категории по её ID."""

    _validate_parent_category(category_id, database)
    sql_query = select(ProductModel).where(
        ProductModel.category_id == category_id,
        ProductModel.is_active == True
    )
    return database.scalars(sql_query).all()

##############################################################################################

@products_router.get(
    path='/{product_id}',
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: int, database: Session = Depends(get_db)) -> ProductSchema:
    """Возвращает детальную информацию о товаре по его ID."""

    _validate_product_by_id(product_id, database)
    sql_query = select(ProductModel).where(ProductModel.id == product_id)
    product = database.scalars(sql_query).first()
    _validate_parent_category(product.category_id, database)

    return product

##############################################################################################

@products_router.put('/{product_id}')
async def update_product(product_id: int):
    """Обновляет товар по его ID."""
    #TODO:

    return {'message': f'Товар {product_id} обновлён (заглушка)'}

##############################################################################################

@products_router.delete('/{product_id}')
async def delete_product(product_id: int):
    """Удаляет товар по его ID."""
    #TODO:

    return {'message': f'Товар {product_id} удалён (заглушка)'}

##############################################################################################
