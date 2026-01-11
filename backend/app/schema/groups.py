from pydantic import BaseModel
from typing import List, Dict, Optional

class CreateGroupModel(BaseModel):
    jwt: str
    name: str
    description: str = ""

class GetGroupInfoModel(BaseModel):
    jwt: str

class UpdateGroupModel(BaseModel):
    jwt: str
    name: Optional[str] = None
    description: Optional[str] = None
    picture_url: Optional[str] = None

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
    users: List[Dict] = [] 

class AssignRoleModel(BaseModel):
    jwt: str
    user_id: str
    role: str 

class LeaveGroupModel(BaseModel):
    jwt: str

class GetUserGroupsModel(BaseModel):
    jwt: str