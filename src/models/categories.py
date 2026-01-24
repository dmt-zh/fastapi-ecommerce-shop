from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.services.database.postgresql import Base

if TYPE_CHECKING:
    from src.models import Product


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    products: Mapped[list['Product']] = relationship(
        back_populates='category',
        cascade='all, delete-orphan',
    )
    parent: Mapped['Category | None'] = relationship(
        back_populates='children',
        remote_side='Category.id',
    )
    children: Mapped[list['Category']] = relationship(back_populates='parent')
