from fastapi import APIRouter, HTTPException
from schema.notes import (
    CheckNoteAccessModel,
    CreateNoteModel,
    DeleteNoteModel,
    GetNoteContentModel,
    GetUserNotesModel,
    RevokeNoteAccessModel,
    ShareNoteModel,
    UpdateNoteModel,
)

router = APIRouter()


# Create new note
# Must be owner of the note or if owned by group, must be admin or owner of the group
@router.post("/api/v1/notes/create", tags=["notes"])
def create_note_api(body: CreateNoteModel):
    pass


# Update existing note
# Must be owner of the note or if owned by group, must be admin or owner of the group
@router.post("/api/v1/notes/update", tags=["notes"])
def update_note_api(body: UpdateNoteModel):
    pass


# Delete existing note
# Must be owner of the note or if owned by group, must be admin or owner of the group
@router.post("/api/v1/notes/delete", tags=["notes"])
def delete_note_api(body: DeleteNoteModel):
    pass


# Get all notes for a user
@router.post("/api/v1/notes/get", tags=["notes"])
def get_user_notes_api(body: GetUserNotesModel):
    pass


# Get note content
@router.post("/api/v1/note/get/{note_id}", tags=["notes"])
def get_note_content_api(note_id: str, body: GetNoteContentModel):
    pass


# Check note access
# Must be owner of the note or if owned by group, must be admin or owner of the group
@router.post("/api/v1/note/access/{note_id}/get", tags=["notes"])
def check_note_access_api(note_id: str, body: CheckNoteAccessModel):
    pass


# Share note with user or group
# Must be owner of the note or if owned by group, must be admin or owner of
@router.post("/api/v1/note/permissions/share/{note_id}", tags=["notes"])
def share_note_api(note_id: str, body: ShareNoteModel):
    pass


# Revoke note access from user or group
# Must be owner of the note or if owned by group, must be admin or owner of
@router.post("/api/v1/note/permissions/revoke/{note_id}", tags=["notes"])
def revoke_note_access_api(note_id: str, body: RevokeNoteAccessModel):
    pass


# Update note permissions for user or group
# Must be owner or admin of the note or if owned by group, must be admin or owner of
@router.post("/api/v1/note/permissions/update/{note_id}", tags=["notes"])
def update_note_permissions_api(note_id: str, body: RevokeNoteAccessModel):
    pass
