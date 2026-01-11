from pydantic import BaseModel


class GetTagModel(BaseModel):
    jwt: str
    name: str
    color: str


class CreateTagModel(BaseModel):
    jwt: str
    name: str
    color: str


class DeleteTagModel(BaseModel):
    jwt: str
    name: str
