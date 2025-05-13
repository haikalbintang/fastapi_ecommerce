from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session, select

from models import User

sqlite_file_name = "database1.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(url=sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

def user_seed():
    with Session(engine) as session:
        statement = select(User).where(User.username == "kopiberry")
        existing_user = session.exec(statement=statement).first()
        if existing_user:
            print("User already exists, skipping seeding...")
            return

        kopi_berry = User(username="kopiberry",
                          email="kopiberry@mail.com",
                          password="1234",
                          full_name="Kopi Berry",
                          role="admin")

        session.add(kopi_berry)

        session.commit()

        session.close()

def main():
    create_db_and_tables()
    user_seed()

if __name__ == "__main__":
    main()