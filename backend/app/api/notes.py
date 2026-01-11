from fastapi import APIRouter, HTTPException
from schema.notes import NoteModel, GetNotesModel, UpdateNoteModel, DeleteNoteModel
from db.querries.notes import create_note, get_user_notes, update_note, delete_note
from core.user import get_jwt_signature_key
import jwt

router = APIRouter()

def get_email_from_token(token: str):
    try:
        key = get_jwt_signature_key()
        payload = jwt.decode(token, key, algorithms=["HS256"])
        return payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/api/v1/notes/create", tags=["notes"])
def create_note_api(body: NoteModel):
    email = get_email_from_token(body.jwt)
    try:
        create_note(body, email)
        return {"message": "Note created successfully"}
    except Exception as e:
        print(f"create_note error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/api/v1/notes/get", tags=["notes"])
def get_notes_api(body: GetNotesModel):
    email = get_email_from_token(body.jwt)
    notes = get_user_notes(email)
    return {"notes": notes}

@router.post("/api/v1/notes/update", tags=["notes"])
def update_note_api(body: UpdateNoteModel):
    email = get_email_from_token(body.jwt)
    try:
        update_note(body, email)
        return {"message": "Note updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/api/v1/notes/delete", tags=["notes"])
def delete_note_api(body: DeleteNoteModel):
    email = get_email_from_token(body.jwt)
    try:
        delete_note(body.note_id, email)
        return {"message": "Note deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))