from fastapi import APIRouter, HTTPException
from schema.groups import (
    AddUserToGroupModel,
    AssignRoleModel,
    CreateGroupModel,
    DeleteGroupModel,
    GetGroupInfoModel,
    GetUserGroupsModel,
    LeaveGroupModel,
    ListGroupMembersModel,
    RemoveUserFromGroupModel,
    UpdateGroupModel,
)

router = APIRouter()


# Create group -> becomes owner
@router.post("/groups/create", tags=["groups"])
def create_group_api(body: CreateGroupModel):
    pass


# Everyone in the group
# Gets group info
@router.post("/groups/{group_id}", tags=["groups"])
def get_group_info_api(group_id: int, body: GetGroupInfoModel):
    pass


# Only owner and admin
# Update group info
@router.put("/groups/{group_id}", tags=["groups"])
def update_group_api(group_id: int, body: UpdateGroupModel):
    pass


# Only owner
# Delete group
@router.delete("/groups/{group_id}", tags=["groups"])
def delete_group_api(group_id: int, body: DeleteGroupModel):
    pass


# Only owner and admin
# Add member to group
@router.post("/groups/{group_id}/members/add", tags=["groups"])
def add_member_to_group_api(group_id: int, body: AddUserToGroupModel):
    pass


# Only owner and admin
# Remove member from group
@router.post("/groups/{group_id}/members/remove", tags=["groups"])
def remove_member_from_group_api(group_id: int, body: RemoveUserFromGroupModel):
    pass


# everyone in the group
# Get group members and their roles
@router.post("/groups/{group_id}/members", tags=["groups"])
def list_group_members_api(group_id: int, body: ListGroupMembersModel):
    pass


# Owner and admin unless owner or admin then only owner
# Assign role to member
@router.post("/groups/{group_id}/roles/assign", tags=["groups"])
def assign_role_api(group_id: int, body: AssignRoleModel):
    pass


# User can leave group
@router.post("/groups/{group_id}/leave", tags=["groups"])
def leave_group_api(group_id: int, body: LeaveGroupModel):
    pass


# Get user's groups
@router.post("/groups/get_user_groups", tags=["groups"])
def get_user_groups_api(body: GetUserGroupsModel):
    pass
