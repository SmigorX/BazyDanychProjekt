import uuid
from sqlalchemy import text
from db.connection import get_connection
from schema.notes import NoteModel, UpdateNoteModel
from datamodels.jwt import TokenModel

def create_note(note_data: NoteModel, email: str):
    conn = get_connection()
    try:
        user_query = text("SELECT id FROM Users WHERE email = :email")
        user_id = conn.execute(user_query, {"email": email}).scalar()

        query = text("""
            INSERT INTO Notes (id, title, content, created_by, group_id, latitude, longitude, color_hex, tags)
            VALUES (:id, :title, :content, :created_by, :group_id, :lat, :lng, :color, :tags)
        """)
        
        lat = 52.23
        lng = 21.01
        color = "#3b82f6"

        for t in note_data.tags:
            try:
                if t.startswith("lat:"):
                    parts = t.split(":", 1)
                    if len(parts) == 2:
                        parsed_lat = float(parts[1])
                        if -90 <= parsed_lat <= 90:
                            lat = parsed_lat
                elif t.startswith("lng:"):
                    parts = t.split(":", 1)
                    if len(parts) == 2:
                        parsed_lng = float(parts[1])
                        if -180 <= parsed_lng <= 180:
                            lng = parsed_lng
                elif t.startswith("col:"):
                    parts = t.split(":", 1)
                    if len(parts) == 2 and len(parts[1]) == 7 and parts[1].startswith("#"):
                        color = parts[1]
            except (ValueError, IndexError):
                continue

        gid = note_data.group_id if note_data.group_id and len(note_data.group_id) > 10 else None

        conn.execute(query, {
            "id": str(uuid.uuid4()),
            "title": note_data.title,
            "content": note_data.content,
            "created_by": user_id,
            "group_id": gid,
            "lat": lat,
            "lng": lng,
            "color": color,
            "tags": note_data.tags
        })
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def get_user_notes(email: str):
    conn = get_connection()
    try:
        user_id_query = text("SELECT id FROM Users WHERE email = :email")
        user_id = conn.execute(user_id_query, {"email": email}).scalar()

        query = text("""
            SELECT DISTINCT n.id, n.title, n.content, n.tags, n.group_id, g.name
            FROM Notes n
            LEFT JOIN Groups g ON n.group_id = g.id AND g.is_deleted = FALSE
            WHERE n.is_deleted = FALSE 
            AND (
                n.created_by = :uid 
                OR n.group_id IN (
                    SELECT group_id FROM Group_Members 
                    WHERE user_id = :uid AND is_active = TRUE
                )
            )
        """)
        
        result = conn.execute(query, {"uid": user_id}).fetchall()
        
        notes = []
        for row in result:
            notes.append({
                "id": str(row[0]),
                "title": row[1],
                "content": row[2],
                "tags": row[3],
                "group_id": str(row[4]) if row[4] else None,
                "group_name": row[5] if row[5] else None 
            })
        return notes
    except Exception as e:
        print(f"Error fetching notes: {e}")
        return []

def update_note(note_data: UpdateNoteModel, email: str):
    conn = get_connection()
    try:
        user_id_query = text("SELECT id FROM Users WHERE email = :email")
        user_id = conn.execute(user_id_query, {"email": email}).scalar()

        check_query = text("""
            SELECT created_by, group_id FROM Notes WHERE id = :nid
        """)
        note_row = conn.execute(check_query, {"nid": note_data.note_id}).fetchone()
        
        if not note_row:
            raise Exception("Note not found")

        is_owner = str(note_row[0]) == str(user_id)
        
        has_group_access = False
        if note_row[1]:
            perm_query = text("SELECT role FROM Group_Members WHERE group_id = :gid AND user_id = :uid AND is_active = TRUE")
            role = conn.execute(perm_query, {"gid": note_row[1], "uid": user_id}).scalar()
            if role in ['owner', 'admin']:
                has_group_access = True

        if not is_owner and not has_group_access:
            raise Exception("Permission denied")

        lat = 52.23
        lng = 21.01
        color = "#3b82f6"
        for t in note_data.tags:
            try:
                if t.startswith("lat:"):
                    parts = t.split(":", 1)
                    if len(parts) == 2:
                        parsed_lat = float(parts[1])
                        if -90 <= parsed_lat <= 90:
                            lat = parsed_lat
                elif t.startswith("lng:"):
                    parts = t.split(":", 1)
                    if len(parts) == 2:
                        parsed_lng = float(parts[1])
                        if -180 <= parsed_lng <= 180:
                            lng = parsed_lng
                elif t.startswith("col:"):
                    parts = t.split(":", 1)
                    if len(parts) == 2 and len(parts[1]) == 7 and parts[1].startswith("#"):
                        color = parts[1]
            except (ValueError, IndexError):
                continue

        gid = note_data.group_id if note_data.group_id and len(note_data.group_id) > 10 else None

        query = text("""
            UPDATE Notes 
            SET title = :title, content = :content, tags = :tags, 
                latitude = :lat, longitude = :lng, color_hex = :col,
                group_id = :gid, updated_at = CURRENT_TIMESTAMP
            WHERE id = :nid
        """)
        conn.execute(query, {
            "title": note_data.title,
            "content": note_data.content,
            "tags": note_data.tags,
            "lat": lat, "lng": lng, "col": color, "gid": gid,
            "nid": note_data.note_id
        })
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def delete_note(note_id: str, email: str):
    conn = get_connection()
    try:
        user_id_query = text("SELECT id FROM Users WHERE email = :email")
        user_id = conn.execute(user_id_query, {"email": email}).scalar()

        check_query = text("SELECT created_by, group_id FROM Notes WHERE id = :nid")
        note_row = conn.execute(check_query, {"nid": note_id}).fetchone()
        
        if not note_row:
            raise Exception("Note not found")

        is_owner = str(note_row[0]) == str(user_id)
        has_group_access = False
        if note_row[1]:
            perm_query = text("SELECT role FROM Group_Members WHERE group_id = :gid AND user_id = :uid AND is_active = TRUE")
            role = conn.execute(perm_query, {"gid": note_row[1], "uid": user_id}).scalar()
            if role in ['owner', 'admin']:
                has_group_access = True

        if not is_owner and not has_group_access:
            raise Exception("Permission denied")

        conn.execute(text("UPDATE Notes SET is_deleted = TRUE WHERE id = :nid"), {"nid": note_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e