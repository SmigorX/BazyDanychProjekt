from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
import uuid

# --- USER ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    description: Optional[str] = None
    profile_picture_url: Optional[str] = None # WF.60
    email: Optional[EmailStr] = None

class PasswordChange(BaseModel): # WB.8
    old_password: str
    new_password: str

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str
    last_name: str
    description: Optional[str] = None
    profile_picture_url: Optional[str] = None
    created_at: datetime
    class Config: from_attributes = True

# --- GRUPY ---
class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    profile_picture_url: Optional[str] = None # WF.92
    creator_user_id: str

class GroupUpdate(BaseModel): # WB.A
    description: Optional[str] = None
    profile_picture_url: Optional[str] = None
    requesting_user_id: str

class MemberAdd(BaseModel):
    user_id_to_add: str
    role: str = "member"
    requesting_user_id: str

class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    profile_picture_url: Optional[str]
    created_at: datetime
    class Config: from_attributes = True

# --- NOTATKI ---
class NoteCreate(BaseModel):
    title: str
    content: str
    color: str = "#FFFFFF"
    latitude: float
    longitude: float
    created_by_user_id: str 
    group_id: Optional[str] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    color: Optional[str] = None
    group_id: Optional[str] = None
    requesting_user_id: str 

class NoteShareCreate(BaseModel): # WB.3 Udostępnianie
    user_id_to_share_with: str
    can_edit: bool = False
    requesting_user_id: str

class NoteResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    color: str
    latitude: float
    longitude: float
    created_at: datetime
    created_by: Optional[uuid.UUID] # Może być None po usunięciu usera
    group_id: Optional[uuid.UUID]
    class Config: from_attributes = True