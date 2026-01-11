from pydantic import BaseModel


class CreateNoteModel(BaseModel):
    jwt: str
    title: str
    content: str
    tags: list[str] = []


class UpdateNoteModel(BaseModel):
    jwt: str
    note_id: str
    title: str
    content: str
    tags: list[str] = []


class DeleteNoteModel(BaseModel):
    jwt: str
    note_id: str


class GetUserNotesModel(BaseModel):
    jwt: str


class GetNoteContentModel(BaseModel):
    jwt: str
    note_id: str


class CheckNoteAccessModel(BaseModel):
    jwt: str
    note_id: str


class ShareNoteModel(BaseModel):
    jwt: str
    note_id: str
    user_id: str
    permission: str  # e.g., 'read', 'write'


class RevokeNoteAccessModel(BaseModel):
    jwt: str
    note_id: str
    user_id: str
