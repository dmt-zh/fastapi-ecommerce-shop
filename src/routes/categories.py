from collections.abc import Mapping, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update

from src.api.auth import is_admin
from src.dependencies import AsyncDatabaseDep
from src.models import Category as CategoryModel, User as UserModel
from src.schemas import Category as CategorySchema, CategoryCreate
from src.utils.routes import _build_category_query, _validate_parent_category

##############################################################################################

router = APIRouter(
    prefix='/categories',
    tags=['categories'],
)

##############################################################################################

@router.get(
    path='/',
    response_model=Sequence[CategorySchema],
)
async def get_all_categories(database: AsyncDatabaseDep) -> Sequence[CategorySchema] | list:
    """Возвращает список всех категорий товаров."""

    sql_query = select(CategoryModel).where(CategoryModel.is_active == True)
    categories = await database.scalars(sql_query)
    return categories.all()

##############################################################################################

@router.post(
    path='/',
    response_model=CategorySchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CategoryCreate,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_admin),
) -> CategorySchema:
    """Создаёт новую категорию."""

    await _validate_parent_category(category, database)
    new_category = CategoryModel(**category.model_dump())
    database.add(new_category)
    await database.commit()

    return new_category

##############################################################################################

@router.put(
    path='/{category_id}',
    response_model=CategorySchema,
)
async def update_category(
    category_id: int,
    category: CategoryCreate,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_admin),
) -> CategorySchema:
    """Обновляет категорию по её ID."""

    sql_query = _build_category_query(category_id)
    categories = await database.scalars(sql_query)
    category_to_update = categories.first()
    if category_to_update is None:
        raise HTTPException(
            status_code=404,
            detail='Category not found',
        )

    await _validate_parent_category(category, database)
    values_to_update = category.model_dump(exclude_unset=True)
    await database.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**values_to_update),
    )
    await database.commit()

    return category_to_update

##############################################################################################

@router.delete(
    path='/{category_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_category(
    category_id: int,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_admin),
) -> Mapping[str, str]:
    """Удаляет категорию по её ID."""

    sql_query = _build_category_query(category_id)
    categories = await database.scalars(sql_query)
    category = categories.first()
    if category is None:
        raise HTTPException(status_code=404, detail='Category not found')

    await database.execute(
        update(CategoryModel).where(CategoryModel.id == category_id).values(is_active=False),
    )
    await database.commit()

    return {'status': 'success', 'message': 'Category marked as inactive'}

##############################################################################################
