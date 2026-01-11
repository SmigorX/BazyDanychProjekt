from pydantic import BaseModel

class TokenModel(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    profile_picture_url: str