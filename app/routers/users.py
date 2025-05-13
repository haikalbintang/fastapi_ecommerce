from typing import Annotated

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select

from db import SessionDep
from models import User, UserPublic, UserUpdate, Product
from app.auth import get_current_active_user


router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[UserPublic])
def read_users(
        session: SessionDep,
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/me")
async def read_me(
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


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
def disable_user(
        user_id: int,
        session: SessionDep,
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    if user.disabled:
        return {"message": "User is already disabled"}

    if user.role == "admin":
        return {"message": "Cannot disable an admin user"}

    user.disabled = True
    session.add(user)
    session.commit()

    return {"message": f"User '{user.username}' has been disabled"}


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
        user_id: int,
        user: UserUpdate,
        session: SessionDep,
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    existing_user = session.get(User, user_id)

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    if existing_user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    existing_user.sqlmodel_update(user.model_dump(exclude_unset=True))
    session.add(existing_user)
    session.commit()
    session.refresh(existing_user)
    return {"updated_user": existing_user}


@router.patch("/{user_id}/enable")
def enable_user(
        user_id: int,
        session: SessionDep,
        current_user: Annotated[User, Depends(get_current_active_user)]
):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to enable this user")

    if not user.disabled:
        return {"message": "User is already active"}

    user.disabled = False
    session.add(user)
    session.commit()

    return {"message": f"User '{user.username}' has been enabled"}


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