from schema.tags import CreateTagModel, DeleteTagModel, GetTagModel


def add_tag_to_note(note_id: int, body: CreateTagModel):
    pass


def get_tags_for_note(note_id: int, body: GetTagModel):
    pass


def remove_tag_from_note(note_id: int, body: DeleteTagModel):
    pass
