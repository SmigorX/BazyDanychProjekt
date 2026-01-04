from pydantic import BaseModel, EmailStr


class NewUserSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    hash: str
