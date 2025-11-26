from collections.abc import Mapping, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql.selectable import Select
from src.models import Category as CategoryModel
from src.schemas import Category as CategorySchema, CategoryCreate
from src.services import get_db

##############################################################################################

categories_router = APIRouter(
    prefix='/categories',
    tags=['categories'],
)

##############################################################################################

def _build_category_query(category: CategoryCreate | int) -> Select:
    """Формируется базовый запрос для извлечения категорий."""

    category_id = category if isinstance(category, int) else category.parent_id
    return select(CategoryModel).where(
        CategoryModel.id == category_id,
        CategoryModel.is_active == True,
    )

##############################################################################################

def _validate_parent_category(category: CategoryCreate, database: Session) -> None:
    """Проверяется наличие родительской категории."""

    if category.parent_id is not None:
        sql_query = _build_category_query(category)
        parent_category = database.scalars(sql_query).first()
        if parent_category is None:
            raise HTTPException(status_code=400, detail='Parent category not found')

##############################################################################################

@categories_router.get(
    path='/',
    response_model=Sequence[CategorySchema],
)
async def get_all_categories(database: Session = Depends(get_db)) -> Sequence[CategorySchema]:
    """Возвращает список всех категорий товаров."""

    sql_query = select(CategoryModel).where(CategoryModel.is_active == True)
    return database.scalars(sql_query).all()

##############################################################################################

@categories_router.post(
    path='/',
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CategoryCreate,
    database: Session = Depends(get_db),
) -> CategorySchema:
    """Создаёт новую категорию."""

    _validate_parent_category(category, database)
    new_category = CategoryModel(**category.model_dump())
    database.add(new_category)
    database.commit()
    database.refresh(new_category)

    return new_category

##############################################################################################

@categories_router.put(
    path='/{category_id}',
    response_model=CategorySchema,
)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    database: Session = Depends(get_db),
) -> CategorySchema:
    """Обновляет категорию по её ID."""

    sql_query = _build_category_query(category_id)
    category_to_update = database.scalars(sql_query).first()
    if category_to_update is None:
        raise HTTPException(
            status_code=404,
            detail='Category not found',
        )

    _validate_parent_category(category, database)

    database.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump()),
    )
    database.commit()
    database.refresh(category_to_update)
    return category_to_update

##############################################################################################

@categories_router.delete(
    path='/{category_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_category(
    category_id: int,
    database: Session = Depends(get_db),
) -> Mapping[str, str]:
    """Удаляет категорию по её ID."""

    sql_query = _build_category_query(category_id)
    category = database.scalars(sql_query).first()
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')

    database.execute(
        update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False),
    )
    database.commit()

    return {'status': 'success', 'message': 'Category marked as inactive'}

##############################################################################################
