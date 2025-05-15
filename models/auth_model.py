from sqlmodel import SQLModel

class PasswordChange(SQLModel):
    old_password: str
    new_password: str

class EmailRequest(SQLModel):
    email: str

class ResetPasswordRequest(SQLModel):
    token: str
    new_password: str