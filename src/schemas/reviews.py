from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

##############################################################################################

class Review(BaseModel):
    """Модель для ответа с данными отзывов по товарам. Используется в GET-запросах."""

    id: int = Field(description='Уникальный идентификатор отзыва')
    user_id: int = Field(description='Уникальный идентификатор пользователя оставившего отзыв')
    product_id: int = Field(description='Уникальный идентификатор товара')
    comment: str | None = Field(default=None, description='Текст отзыва по товару')
    comment_date: datetime = Field(description='Дата оставления отзыва')
    grade: int = Field(description='Оценка пользователя по товару')
    is_active: bool = Field(description='Является ли отзыв активным или удаленным.')
    model_config = ConfigDict(from_attributes=True)

##############################################################################################

class ReviewCreate(BaseModel):
    """Модель для создания и обновления отзывов по товарам. Используется в POST и PUT запросах."""

    product_id: int = Field(description='Уникальный идентификатор товара')
    comment: str | None = Field(default=None, description='Текст отзыва по товару')
    grade: int = Field(ge=1, le=5, description='Оценка пользователя по товару')

##############################################################################################
