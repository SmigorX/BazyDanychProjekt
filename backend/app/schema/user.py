from pydantic import BaseModel
from typing import Optional

class NewUserSchema(BaseModel):
    email: str
    first_name: str
    last_name: str
    hash: str

class LoginUserSchema(BaseModel):
    email: str
    hash: str

class UpdateUserSchema(BaseModel):
    email: str
    first_name: str
    last_name: str
    profile_picture: Optional[str] = None
    description: Optional[str] = "" 

class UpdateUserPasswordSchema(BaseModel):
    email: str
    hash: str

class GetUserDataSchema(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    profile_picture: Optional[str] = None
    description: Optional[str] = "" 