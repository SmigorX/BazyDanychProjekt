from pydantic import BaseModel


class CreateGroupModel(BaseModel):
    jwt: str
    name: str
    description: str


class GetGroupInfoModel(BaseModel):
    jwt: str


class UpdateGroupModel(BaseModel):
    jwt: str
    name: str
    description: str
    picture_url: str


class DeleteGroupModel(BaseModel):
    jwt: str


class AddUserToGroupModel(BaseModel):
    jwt: str
    user_id: str


class RemoveUserFromGroupModel(BaseModel):
    jwt: str
    user_id: str


class ListGroupMembersModel(BaseModel):
    jwt: str
    users: list[dict]


class AssignRoleModel(BaseModel):
    jwt: str
    user_id: str
    role: str


class LeaveGroupModel(BaseModel):
    jwt: str


class GetUserGroupsModel(BaseModel):
    jwt: str
