from collections.abc import Mapping, Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, or_, select, update

from src.api.auth import is_authorized
from src.dependencies import AsyncDatabaseDep
from src.models import Product as ProductModel, User as UserModel
from src.schemas import Product as ProductSchema, ProductCreate, ProductList, ProductsRequest
from src.utils.routes import _validate_parent_category, _validate_product_by_id

router = APIRouter(prefix='/products', tags=['products'])


@router.get(
    path='/',
    response_model=ProductList,
)
async def get_all_products(
    request: Annotated[ProductsRequest, Query()],
    database: AsyncDatabaseDep,
) -> Mapping[str, Sequence[ProductModel] | int]:
    """Возвращает список всех активных товаров."""
    if request.min_price is not None and request.max_price is not None and request.min_price > request.max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='"min_price"не может быть больше "max_price"',
        )

    filters = [ProductModel.is_active == True]

    if request.category_id is not None:
        filters.append(ProductModel.category_id == request.category_id)
    if request.min_price is not None:
        filters.append(ProductModel.price >= request.min_price)
    if request.max_price is not None:
        filters.append(ProductModel.price <= request.max_price)
    if request.in_stock is not None:
        filters.append(ProductModel.stock > 0 if request.in_stock else ProductModel.stock == 0)
    if request.seller_id is not None:
        filters.append(ProductModel.seller_id == request.seller_id)

    sql_query = select(func.count()).select_from(ProductModel).where(*filters)

    rank_col = None
    if request.search:
        search_value = request.search.strip()
        if search_value:
            ts_query_en = func.websearch_to_tsquery('english', search_value)
            ts_query_ru = func.websearch_to_tsquery('russian', search_value)
            ts_match_any = or_(
                ProductModel.tsv.op('@@')(ts_query_en),
                ProductModel.tsv.op('@@')(ts_query_ru),
            )
            filters.append(ts_match_any)
            rank_col = func.greatest(
                func.ts_rank_cd(ProductModel.tsv, ts_query_en),
                func.ts_rank_cd(ProductModel.tsv, ts_query_ru),
            ).label('rank')
            sql_query = select(func.count()).select_from(ProductModel).where(*filters)

    total = await database.scalar(sql_query) or 0

    if rank_col is not None:
        products_query = select(ProductModel, rank_col) \
            .where(*filters) \
            .order_by(desc(rank_col), ProductModel.id) \
            .offset((request.page - 1) * request.page_size) \
            .limit(request.page_size)

        rows = (await database.execute(products_query)).all()
        items: Sequence[ProductModel] = [row[0] for row in rows]

    else:
        products_query = select(ProductModel) \
            .where(*filters) \
            .order_by(ProductModel.id) \
            .offset((request.page - 1) * request.page_size) \
            .limit(request.page_size)

        items = (await database.scalars(products_query)).all()

    return {
        'items': items,
        'total': total,
        'page': request.page,
        'page_size': request.page_size,
    }


@router.get(
    path='/{product_id}',
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: int, database: AsyncDatabaseDep) -> ProductModel:
    """Возвращает детальную информацию о товаре по его ID."""
    product = await _validate_product_by_id(product_id, database)
    await _validate_parent_category(product.category_id, database)

    return product


@router.get(
    path='/category/{category_id}',
    response_model=Sequence[ProductSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products_by_category(
    category_id: int,
    database: AsyncDatabaseDep,
) -> Sequence[ProductModel]:
    """Возвращает список товаров в указанной категории по её ID."""
    await _validate_parent_category(category_id, database)
    sql_query = select(ProductModel).where(
        ProductModel.category_id == category_id,
        ProductModel.is_active == True,
    )
    products = await database.scalars(sql_query)

    return products.all()


@router.post(
    path='/',
    response_model=ProductSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product: ProductCreate,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('seller',))),
) -> ProductModel:
    """Создаёт новый товар."""
    await _validate_parent_category(product.category_id, database)
    new_product = ProductModel(**product.model_dump(), seller_id=current_user.id)
    database.add(new_product)
    await database.commit()
    await database.refresh(new_product)

    return new_product


@router.put(
    path='/{product_id}',
    response_model=ProductSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: int,
    product: ProductCreate,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('seller',))),
) -> ProductModel:
    """Обновляет товар по его ID."""
    product_to_update = await _validate_product_by_id(product_id, database)
    await _validate_parent_category(product.category_id, database)

    if product_to_update.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can only update your own products',
        )

    await database.execute(
        update(ProductModel)
        .where(ProductModel.id == product_id)
        .values(**product.model_dump()),
    )
    await database.commit()
    await database.refresh(product_to_update)

    return product_to_update


@router.delete(
    path='/{product_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_product(
    product_id: int,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('seller',))),
) -> Mapping[str, str]:
    """Удаляет товар по его ID."""
    product_to_delete = await _validate_product_by_id(product_id, database)
    if product_to_delete.seller_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can only delete your own products',
        )

    await database.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(is_active=False),
    )
    await database.commit()
    await database.refresh(product_to_delete)

    return {'status': 'success', 'message': f'Product with id [{product_id}] marked as inactive'}
