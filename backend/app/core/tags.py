import uuid
from sqlalchemy import text
from db.connection import get_connection
from core.user import verify_jwt_token, get_jwt_signature_key
from schema.tags import CreateTagModel, DeleteTagModel, GetTagModel
import jwt


def get_email_from_token(token: str):
    try:
        key = get_jwt_signature_key()
        payload = jwt.decode(token, key, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


def get_user_id_by_email(conn, email):
    query = text("SELECT id FROM Users WHERE email = :email")
    user_id = conn.execute(query, {"email": email}).scalar()
    if not user_id:
        raise Exception("User not found")
    return str(user_id)


def check_note_access(conn, note_id, user_id):
    """Check if user has access to the note (owner or group member)"""
    query = text("""
        SELECT n.created_by, n.group_id
        FROM Notes n
        WHERE n.id = :note_id AND n.is_deleted = FALSE
    """)
    result = conn.execute(query, {"note_id": note_id}).fetchone()

    if not result:
        raise Exception("Note not found")

    created_by, group_id = result

    if str(created_by) == str(user_id):
        return True

    if group_id:
        perm_query = text("""
            SELECT role FROM Group_Members
            WHERE group_id = :gid AND user_id = :uid AND is_active = TRUE
        """)
        role = conn.execute(perm_query, {"gid": group_id, "uid": user_id}).scalar()
        if role:
            return True

    raise Exception("Permission denied")


def add_tag_to_note(note_id: str, body: CreateTagModel):
    conn = get_connection()
    try:
        email = get_email_from_token(body.jwt)
        user_id = get_user_id_by_email(conn, email)
        check_note_access(conn, note_id, user_id)

        # Check if tag exists for this user, create if not
        tag_query = text("""
            SELECT id FROM Tags
            WHERE name = :name AND created_by = :user_id
        """)
        tag_id = conn.execute(tag_query, {"name": body.name, "user_id": user_id}).scalar()

        if not tag_id:
            tag_id = str(uuid.uuid4())
            insert_tag = text("""
                INSERT INTO Tags (id, name, color_hex, created_by)
                VALUES (:id, :name, :color, :user_id)
            """)
            conn.execute(insert_tag, {
                "id": tag_id,
                "name": body.name,
                "color": body.color,
                "user_id": user_id
            })

        # Link tag to note
        link_query = text("""
            INSERT INTO Note_Tags (note_id, tag_id)
            VALUES (:note_id, :tag_id)
            ON CONFLICT (note_id, tag_id) DO NOTHING
        """)
        conn.execute(link_query, {"note_id": note_id, "tag_id": tag_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e


def get_tags_for_note(note_id: str, body: GetTagModel):
    conn = get_connection()
    try:
        email = get_email_from_token(body.jwt)
        user_id = get_user_id_by_email(conn, email)
        check_note_access(conn, note_id, user_id)

        query = text("""
            SELECT t.id, t.name, t.color_hex
            FROM Tags t
            JOIN Note_Tags nt ON t.id = nt.tag_id
            WHERE nt.note_id = :note_id
        """)
        result = conn.execute(query, {"note_id": note_id}).fetchall()

        tags = []
        for row in result:
            tags.append({
                "id": str(row[0]),
                "name": row[1],
                "color": row[2]
            })
        return tags
    except Exception as e:
        raise e


def remove_tag_from_note(note_id: str, body: DeleteTagModel):
    conn = get_connection()
    try:
        email = get_email_from_token(body.jwt)
        user_id = get_user_id_by_email(conn, email)
        check_note_access(conn, note_id, user_id)

        # Find tag by name
        tag_query = text("SELECT id FROM Tags WHERE name = :name")
        tag_id = conn.execute(tag_query, {"name": body.name}).scalar()

        if not tag_id:
            raise Exception("Tag not found")

        # Remove link
        delete_query = text("""
            DELETE FROM Note_Tags
            WHERE note_id = :note_id AND tag_id = :tag_id
        """)
        conn.execute(delete_query, {"note_id": note_id, "tag_id": tag_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
