from typing import Annotated

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select

from db import SessionDep
from models import User, UserPublic, UserCreate, UserUpdate, Product
from ..dependencies import get_token_header


router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=UserPublic, status_code=201)
def create_user(user: UserCreate, session: SessionDep):
    existing_username = session.exec(select(User).where(User.username == user.username)).first()
    if existing_username:
        raise HTTPException(status_code=409, detail="Username already exist")
    existing_email = session.exec(select(User).where(User.email == user.email)).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already exist")
    try:
        new_user = User(**user.model_dump())
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[UserPublic])
def read_users(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/{user_id}", response_model=UserPublic)
def read_user(
        user_id: int,
        session: SessionDep,
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}

@router.delete("/{user_id}")
def delete_user(
        user_id: int,
        session: SessionDep
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
        user_id: int,
        user: UserUpdate,
        session: SessionDep
):
    existing_user = session.get(User, user_id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_user.sqlmodel_update(user.model_dump(exclude_unset=True))
    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return {"updated_user": existing_user}


@router.get("/{user_id}/products")
def read_user_products(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    products = session.exec(select(Product).where(Product.merchant_id == user_id)).all()

    return {
        **user.model_dump(exclude={"password"}),
        "products": products
    }