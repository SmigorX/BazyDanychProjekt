from pydantic import BaseModel, EmailStr


class NewUserSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    hash: str


class LoginUserSchema(BaseModel):
    email: EmailStr
    hash: str


class UpdateUserSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    description: str
    profile_picture: str


class UpdateUserPasswordSchema(BaseModel):
    email: EmailStr
    hash: str


class GetUserDataSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    description: str
    profile_picture: str
    id: int
