from core.tags import add_tag_to_note, get_tags_for_note, remove_tag_from_note
from fastapi import APIRouter, HTTPException
from schema.tags import CreateTagModel, DeleteTagModel, GetTagModel

router = APIRouter()


# Must have write or admin access to the note, or be admin or owner of group with that access
@router.post("/api/v1/tags/get/{note_id}", tags=["tags"])
def get_tags(note_id: int, body: GetTagModel):
    try:
        tags = get_tags_for_note(note_id, body)
        return {"tags": tags}
    except Exception as e:
        print(f"get_tags api error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/v1/tags/add/{note_id}", tags=["tags"])
def add_tag(note_id: int, body: CreateTagModel):
    try:
        add_tag_to_note(note_id, body)
        return {"message": "Tag added successfully"}
    except Exception as e:
        print(f"add_tag api error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/v1/tags/remove/{note_id}", tags=["tags"])
def remove_tag(note_id: int, body: DeleteTagModel):
    try:
        remove_tag_from_note(note_id, body)
        return {"message": "Tag removed successfully"}
    except Exception as e:
        print(f"remove_tag api error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
