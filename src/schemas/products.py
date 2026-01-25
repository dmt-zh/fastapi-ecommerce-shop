from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    """Модель для ответа с данными товара. Используется в GET-запросах."""

    id: int = Field(description='Уникальный идентификатор товара')
    name: str = Field(description='Название товара')
    description: str | None = Field(
        default=None,
        description='Описание товара',
    )
    price: Decimal = Field(
        gt=0,
        decimal_places=2,
        description='Цена товара в рублях',
    )
    image_url: str | None = Field(
        default=None,
        description='URL изображения товара',
    )
    stock: int = Field(description='Количество товара на складе')
    category_id: int = Field(description='ID категории')
    rating: float = Field(description='Рейтинг товара')
    is_active: bool = Field(description='Активность товара')
    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """Модель для создания и обновления товара. Используется в POST и PUT запросах."""

    name: str = Field(
        min_length=3,
        max_length=100,
        description='Название товара (3-100 символов)',
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description='Описание товара (до 500 символов)',
    )
    price: Decimal = Field(
        gt=0,
        decimal_places=2,
        description='Цена товара (больше 0)',
    )
    image_url: str | None = Field(
        default=None,
        max_length=200,
        description='URL изображения товара',
    )
    stock: int = Field(
        ge=0,
        description='Количество товара на складе (0 или больше)',
    )
    category_id: int = Field(description='ID категории, к которой относится товар')


class ProductList(BaseModel):
    """Список пагинации для товаров."""

    items: list[Product] = Field(description='Товары для текущей страницы')
    total: int = Field(ge=0, description='Общее количество товаров')
    page: int = Field(ge=1, description='Номер текущей страницы')
    page_size: int = Field(ge=1, description='Количество элементов на странице')
    model_config = ConfigDict(from_attributes=True)


class ProductsRequest(BaseModel):
    """Запрос для формирования пагинации по товарам."""

    page: int = Field(ge=1, default=1, description='Номер страницы для пагинации')
    page_size: int = Field(ge=1, le=100, default=20, description='Количество товаров на одной странице')
    category_id: int | None = Field(None, description='ID категории для фильтрации')
    search: str | None = Field(None, min_length=1, description='Поиск по названию товара')
    min_price: float | None = Field(None, ge=0, description='Минимальная цена товара')
    max_price: float | None = Field(None, ge=0, description='Максимальная цена товара')
    in_stock: bool | None = Field(None, description='true — только товары в наличии, false — только без остатка')
    seller_id: int | None = Field(None, description='ID продавца для фильтрации')
