from collections.abc import Mapping, Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update

from src.api.auth import is_authorized
from src.dependencies import AsyncDatabaseDep
from src.models import Review as ReviewModel, User as UserModel
from src.routes.products import router as products_router
from src.schemas import Review as ReviewSchema, ReviewCreate
from src.utils.routes import _update_product_rating, _validate_parent_category, _validate_product_by_id

##############################################################################################

router = APIRouter(
    prefix='/reviews',
    tags=['reviews'],
)

##############################################################################################

@router.get(
    path='/',
    response_model=Sequence[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_all_reviews(database: AsyncDatabaseDep) -> Sequence[ReviewModel]:
    """Возвращает список всех отзывов по товарам."""

    sql_query = select(ReviewModel).where(ReviewModel.is_active == True)
    reviews = await database.scalars(sql_query)
    return reviews.all()

##############################################################################################

@products_router.get(
    path='/{product_id}/reviews/',
    response_model=Sequence[ReviewSchema],
    status_code=status.HTTP_200_OK,
)
async def get_reviews_by_product_id(product_id: int, database: AsyncDatabaseDep) -> Sequence[ReviewModel]:
    """Возвращает список всех отзывов о товаре по его ID."""

    product = await _validate_product_by_id(product_id, database)
    await _validate_parent_category(product.category_id, database)

    sql_query = select(ReviewModel).where(
        ReviewModel.product_id == product_id,
        ReviewModel.is_active == True,
    )
    reviews = await database.scalars(sql_query)
    return reviews.all()

##############################################################################################

@router.post(
    path='/',
    response_model=ReviewSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    review: ReviewCreate,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('buyer',))),
) -> ReviewModel:
    """Создаёт новый отзыв о товаре."""

    product = await _validate_product_by_id(review.product_id, database)
    await _validate_parent_category(product.category_id, database)

    sql_query = select(ReviewModel).where(
        ReviewModel.user_id == current_user.id,
        ReviewModel.product_id == review.product_id,
        ReviewModel.is_active == True,
    )
    review_exists = await database.scalar(sql_query)
    if review_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can save the review for the same product only once',
        )

    new_review = ReviewModel(**review.model_dump(), user_id=current_user.id)
    database.add(new_review)
    await database.commit()
    await database.refresh(new_review)
    await _update_product_rating(product_id=review.product_id, database=database)

    return new_review

#############################################################################################

@router.delete(
    path='/{review_id}',
    status_code=status.HTTP_200_OK,
)
async def delete_review(
    review_id: int,
    database: AsyncDatabaseDep,
    current_user: UserModel = Depends(is_authorized(permissions=('buyer', 'admin'))),
) -> Mapping[str, str]:
    """Удаляет товар по его ID."""

    sql_query = select(ReviewModel).where(
        ReviewModel.id == review_id,
        ReviewModel.is_active == True,
    )
    review_to_delete = await database.scalar(sql_query)
    if review_to_delete is None:
        raise HTTPException(status_code=404, detail='Review not found')

    if current_user.role == 'buyer' and current_user.id != review_to_delete.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can only delete your own reviews',
        )

    await database.execute(
        update(ReviewModel).where(ReviewModel.id == review_id).values(is_active=False),
    )
    await database.commit()
    await database.refresh(review_to_delete)
    await _update_product_rating(product_id=review_to_delete.product_id, database=database)

    return {'status': 'success', 'message': f'Review with ID [{review_id}] is deleted'}

#############################################################################################
