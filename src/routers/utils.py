
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select

from src.models import Category as CategoryModel, Product as ProductModel
from src.schemas import CategoryCreate

##############################################################################################

def _build_category_query(category: CategoryCreate | int) -> Select:
    """Формируется базовый запрос для извлечения категорий."""

    category_id = category if isinstance(category, int) else category.parent_id
    return select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True,
    )

##############################################################################################

def _validate_parent_category(category: CategoryCreate | int, database: Session) -> None:
    """Проверяется наличие родительской категории."""

    if isinstance(category, CategoryCreate) and category.parent_id is None:
        return

    sql_query = _build_category_query(category)
    parent_category = database.scalars(sql_query).first()
    if parent_category is None:
        raise HTTPException(status_code=400, detail='Parent category not found')

##############################################################################################

def _validate_product_by_id(product_id: int, database: Session) -> ProductModel | None:
    """Проверяется наличие товара по указанному идентификатору."""

    sql_query = select(ProductModel).where(
        ProductModel.id == product_id,
        ProductModel.is_active == True,
    )
    product_item = database.scalars(sql_query).first()
    if product_item is None:
        raise HTTPException(status_code=404, detail='Product not found')
    return product_item

##############################################################################################
