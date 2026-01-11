from pydantic import BaseModel, EmailStr


class NewUserModel(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class LoginUserModel(BaseModel):
    email: EmailStr
    password: str


class UpdateUserModel(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    profile_picture: str
    description: str
    jwt: str


class UpdateUserPasswordModel(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str
    jwt: str


class DeleteUserModel(BaseModel):
    jwt: str
    password: str 