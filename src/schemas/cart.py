from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.products import Product


class CartItemBase(BaseModel):
    """Базовая модель, которая содержит минимальный набор полей."""

    product_id: int = Field(description='ID товара')
    quantity: int = Field(ge=1, description='Количество товара')


class CartItemCreate(CartItemBase):
    """Модель для добавления нового товара в корзину."""


class CartItemUpdate(BaseModel):
    """Модель для обновления количества товара в корзине."""

    quantity: int = Field(ge=1, description='Новое количество товара')


class CartItem(BaseModel):
    """Товар в корзине с данными продукта."""

    id: int = Field(description='ID позиции корзины')
    quantity: int = Field(ge=1, description='Количество товара')
    product: Product = Field(description='Информация о товаре')

    model_config = ConfigDict(from_attributes=True)


class Cart(BaseModel):
    """Полная информация о корзине пользователя."""

    user_id: int = Field(description='ID пользователя')
    items: list[CartItem] = Field(default_factory=list, description='Содержимое корзины')
    total_quantity: int = Field(ge=0, description='Общее количество товаров')
    total_price: Decimal = Field(ge=0, description='Общая стоимость товаров')

    model_config = ConfigDict(from_attributes=True)
