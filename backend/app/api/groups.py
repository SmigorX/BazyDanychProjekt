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
from db.querries.groups import (
    create_group, get_group_info, update_group, delete_group,
    add_member, remove_member, list_members, assign_role, 
    leave_group, get_user_groups
)
from core.user import get_jwt_signature_key
import jwt

router = APIRouter()

def get_email_from_token(token: str):
    try:
        key = get_jwt_signature_key()
        payload = jwt.decode(token, key, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/groups/create", tags=["groups"])
def create_group_api(body: CreateGroupModel):
    email = get_email_from_token(body.jwt)
    try:
        gid = create_group(body, email)
        return {"message": "Group created", "group_id": gid}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/groups/get_user_groups", tags=["groups"])
def get_user_groups_api(body: GetUserGroupsModel):
    email = get_email_from_token(body.jwt)
    try:
        groups = get_user_groups(email)
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/groups/{group_id}", tags=["groups"])
def get_group_info_api(group_id: str, body: GetGroupInfoModel):
    email = get_email_from_token(body.jwt)
    try:
        info = get_group_info(group_id, email)
        return info
    except Exception as e:
        raise HTTPException(404, str(e))

@router.put("/groups/{group_id}", tags=["groups"])
def update_group_api(group_id: str, body: UpdateGroupModel):
    email = get_email_from_token(body.jwt)
    try:
        update_group(group_id, body, email)
        return {"message": "Group updated"}
    except Exception as e:
        raise HTTPException(403, str(e))

@router.delete("/groups/{group_id}", tags=["groups"])
def delete_group_api(group_id: str, body: DeleteGroupModel):
    email = get_email_from_token(body.jwt)
    try:
        delete_group(group_id, email)
        return {"message": "Group deleted"}
    except Exception as e:
        raise HTTPException(403, str(e))

@router.post("/groups/{group_id}/members/add", tags=["groups"])
def add_member_to_group_api(group_id: str, body: AddUserToGroupModel):
    email = get_email_from_token(body.jwt)
    try:
        add_member(group_id, body.user_id, email)
        return {"message": "Member added"}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/groups/{group_id}/members/remove", tags=["groups"])
def remove_member_from_group_api(group_id: str, body: RemoveUserFromGroupModel):
    email = get_email_from_token(body.jwt)
    try:
        remove_member(group_id, body.user_id, email)
        return {"message": "Member removed"}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/groups/{group_id}/members", tags=["groups"])
def list_group_members_api(group_id: str, body: ListGroupMembersModel):
    email = get_email_from_token(body.jwt)
    try:
        members = list_members(group_id, email)
        return {"members": members}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/groups/{group_id}/roles/assign", tags=["groups"])
def assign_role_api(group_id: str, body: AssignRoleModel):
    email = get_email_from_token(body.jwt)
    try:
        assign_role(group_id, body.user_id, body.role, email)
        return {"message": "Role assigned"}
    except Exception as e:
        raise HTTPException(403, str(e))

@router.post("/groups/{group_id}/leave", tags=["groups"])
def leave_group_api(group_id: str, body: LeaveGroupModel):
    email = get_email_from_token(body.jwt)
    try:
        leave_group(group_id, email)
        return {"message": "Left group"}
    except Exception as e:
        raise HTTPException(400, str(e))