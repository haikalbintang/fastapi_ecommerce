from typing import Annotated
import os

from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session, select

from models import User
from app.security import get_password_hash


# === Database Config ===
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/fastapidb")

engine = create_engine(
    url=DATABASE_URL,
    echo=True,
)


# === Session Dependency ===
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]


# === DB Init & Seeding ===
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def user_seed():
    """Seed initial admin user if not exists."""
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "kopiberry")).first()
        if user:
            print("User already exists, skipping seeding...")
            return

        hashed_password = get_password_hash("1234")
        session.add(User(
            username="kopiberry",
            email="kopiberry@mail.com",
            hashed_password=hashed_password,
            full_name="Kopi Berry",
            role="admin"
        ))

        session.commit()
        print("Seeded admin user: kopiberry")


async def get_user_by_username(username: str, session: SessionDep) -> User | None:
    """Retrieve user by username."""
    return session.exec(select(User).where(User.username == username)).first()


async def get_user_by_email(email: str, session: SessionDep) -> User | None:
    """Retrieve user by email."""
    return session.exec(select(User).where(User.email == email)).first()


async def create_user(user_data: User, session: SessionDep) -> User:
    """Create a new user from user_data."""
    new_user = User(**user_data.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


# === Entrypoint ===
def main():
    create_db_and_tables()
    user_seed()

if __name__ == "__main__":
    main()
