from typing import TYPE_CHECKING, Optional, List
from enum import Enum

from sqlmodel import SQLModel, Field, Relationship


# if TYPE_CHECKING:
#     from .product_model import Product


class UserRole(str, Enum):
    admin = "admin"
    cashier = "cashier"
    customer = "customer"


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: str
    phone: str | None
    address: str | None
    picture: str | None
    role: UserRole = UserRole.customer
    disabled: bool = False


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    # products: List["Product"] = Relationship(back_populates="merchant")


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    hashed_password: str


class UserUpdate(UserBase):
    hashed_password: str | None


# class UserProducts(UserBase):
#     products: list[Product]