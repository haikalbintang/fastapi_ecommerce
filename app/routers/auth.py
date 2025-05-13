from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel

from models import User, UserCreate, UserPublic
from app import security
from db import SessionDep, get_user_by_username, get_user_by_email, create_user


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, session: SessionDep):
    if await get_user_by_username(user.username, session):
        raise HTTPException(status_code=400, detail="Username already registered")

    if await get_user_by_email(user.email, session):
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        new_user = User(**user.model_dump(exclude={"hashed_password"}))
        new_user.hashed_password = security.get_password_hash(user.hashed_password)
        created_user = await create_user(new_user, session)
        return created_user
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to register user.")


@router.post("/token", response_model=Token)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDep,
):
    user = await get_user_by_username(form_data.username, session)

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")