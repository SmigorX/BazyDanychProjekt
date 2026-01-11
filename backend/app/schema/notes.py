from pydantic import BaseModel
from typing import List, Optional

class NoteModel(BaseModel):
    jwt: str
    title: str
    content: str
    tags: List[str] = []
    group_id: Optional[str] = None

class UpdateNoteModel(BaseModel):
    jwt: str
    note_id: str
    title: str
    content: str
    tags: List[str]
    group_id: Optional[str] = None

class GetNotesModel(BaseModel):
    jwt: str

class DeleteNoteModel(BaseModel):
    jwt: str
    note_id: str