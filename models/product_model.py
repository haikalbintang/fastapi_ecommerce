from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

# if TYPE_CHECKING:
#     from .user_model import User

class ProductBase(SQLModel):
    name: str = Field(index=True)
    price: int = Field(index=True)
    description: str | None
    image: str | None


class Product(ProductBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    merchant_id: int | None = Field(default=None, foreign_key="user.id")
    # merchant: Optional["User"] = Relationship(back_populates="products")