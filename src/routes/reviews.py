from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from src.api.auth import is_buyer
from src.dependencies import AsyncDatabaseDep
from src.models import Review as ReviewModel, User as UserModel
from src.schemas import Review as ReviewSchema, ReviewCreate
from src.utils.routes import _validate_product_by_id

##############################################################################################

router = APIRouter(
    prefix='/reviews',
    tags=['reviews'],
)

##############################################################################################

@router.get(
    path='/',
    response_model=Sequence[ReviewSchema],
)
async def get_all_reviews(database: AsyncDatabaseDep) -> Sequence[ReviewSchema] | list:
    """Возвращает список всех товаров."""

    sql_query = select(ReviewModel).where(ReviewModel.is_active == True)
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
    current_user: UserModel = Depends(is_buyer),
) -> ReviewSchema:
    """Создаёт новый отзыв о товаре."""

    await _validate_product_by_id(review.product_id, database)

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

    return new_review

#############################################################################################
