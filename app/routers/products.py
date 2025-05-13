from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select

from db import SessionDep
from models import ProductBase, Product, User
from app.auth import get_current_active_user


router = APIRouter(
    prefix="/products",
    tags=["products"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


fake_products_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
        product: ProductBase,
        session: SessionDep,
        current_user: User = Depends(get_current_active_user),
):
    new_product = Product(**product.model_dump(exclude={"merchant_id"}))
    new_product.merchant_id = current_user.id
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product


@router.get("/")
async def read_products(
        session: SessionDep,
        offset: int = 0,
        limit: int = 100,
) -> list[Product]:
    products = session.exec(select(Product).offset(offset).limit(limit)).all()
    return products


@router.get("/test")
def select_product_test_6(session: SessionDep):
    products = []
    users = []
    results = session.exec(select(Product, User).join(User, isouter=True))
    for product, user in results:
        products.append(product)
        users.append(user)
    return {"product": products, "user": users}


@router.get("/{product_id}")
async def read_product(
        product_id: int,
        session: SessionDep,
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"product": product}


@router.delete("/{product_id}")
async def delete_product(
        product_id: int,
        session: SessionDep,
        current_user: User = Depends(get_current_active_user),
):
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if current_user.role != "admin" and product.merchant_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    session.delete(product)
    session.commit()
    return {"message": "Product deleted successfully"}


@router.put(
    "/{product_id}",
    responses={403: {"description": "Operation forbidden"}},
)
async def update_product(
        product_id: int,
        product: ProductBase,
        session: SessionDep,
):
    existing_product = session.get(Product, product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    existing_product.sqlmodel_update(product.model_dump(exclude_unset=True))
    session.add(existing_product)
    session.commit()
    session.refresh(existing_product)
    return {"updated_product": existing_product}
