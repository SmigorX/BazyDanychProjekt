from pydantic import BaseModel, EmailStr


class TokenModel(BaseModel):
    email: EmailStr
    profile_picture_url: str
    first_name: str
    last_name: str
