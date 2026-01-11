import uuid
from sqlalchemy import text
from db.connection import get_connection

def get_user_id_by_email(conn, email):
    query = text("SELECT id FROM Users WHERE email = :email")
    user_id = conn.execute(query, {"email": email}).scalar()
    if not user_id:
        raise Exception("User not found")
    return str(user_id)

def check_permission(conn, group_id, user_id, allowed_roles=['owner', 'admin']):
    """Sprawdza czy użytkownik ma odpowiednią rolę w grupie"""
    query = text("""
        SELECT role FROM Group_Members 
        WHERE group_id = :gid AND user_id = :uid AND is_active = TRUE
    """)
    role = conn.execute(query, {"gid": group_id, "uid": user_id}).scalar()
    
    if not role:
        raise Exception("User is not a member of this group")
    if role not in allowed_roles:
        raise Exception(f"Permission denied. Required: {allowed_roles}")
    return role


def create_group(data, creator_email):
    conn = get_connection()
    try:
        user_id = get_user_id_by_email(conn, creator_email)
        group_id = str(uuid.uuid4())

        conn.execute(text("""
            INSERT INTO Groups (id, name, description, created_by)
            VALUES (:id, :name, :desc, :creator)
        """), {"id": group_id, "name": data.name, "desc": data.description, "creator": user_id})

        conn.execute(text("""
            INSERT INTO Group_Members (group_id, user_id, role)
            VALUES (:gid, :uid, 'owner')
        """), {"gid": group_id, "uid": user_id})

        conn.commit()
        return group_id
    except Exception as e:
        conn.rollback()
        raise e

def get_group_info(group_id, email):
    conn = get_connection()
    try:
        user_id = get_user_id_by_email(conn, email)
        
       
        query = text("""
            SELECT g.id, g.name, g.description, g.picture_url, g.created_by, gm.role
            FROM Groups g
            LEFT JOIN Group_Members gm ON g.id = gm.group_id AND gm.user_id = :uid AND gm.is_active = TRUE
            WHERE g.id = :gid AND g.is_deleted = FALSE
        """)
        row = conn.execute(query, {"gid": group_id, "uid": user_id}).fetchone()
        
        if not row:
            raise Exception("Group not found")

        return {
            "id": str(row[0]),
            "name": row[1],
            "description": row[2],
            "picture_url": row[3],
            "created_by": str(row[4]),
            "user_role": row[5] 
        }
    except Exception as e:
        print(f"Error fetching group info: {e}")
        raise e

def update_group(group_id, data, email):
    conn = get_connection()
    try:
        user_id = get_user_id_by_email(conn, email)
        check_permission(conn, group_id, user_id, ['owner', 'admin'])

        query = text("""
            UPDATE Groups 
            SET name = COALESCE(:name, name), 
                description = COALESCE(:desc, description),
                picture_url = COALESCE(:pic, picture_url),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :gid
        """)
        conn.execute(query, {
            "gid": group_id, 
            "name": data.name, 
            "desc": data.description, 
            "pic": data.picture_url
        })
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def delete_group(group_id, email):
    conn = get_connection()
    try:
        user_id = get_user_id_by_email(conn, email)
        check_permission(conn, group_id, user_id, ['owner']) 
        conn.execute(text("UPDATE Groups SET is_deleted = TRUE WHERE id = :gid"), {"gid": group_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def add_member(group_id, target_user_id, requester_email):
    conn = get_connection()
    try:
        req_id = get_user_id_by_email(conn, requester_email)
        check_permission(conn, group_id, req_id, ['owner', 'admin'])

        query = text("""
            INSERT INTO Group_Members (group_id, user_id, role)
            VALUES (:gid, :uid, 'member')
            ON CONFLICT (group_id, user_id) 
            DO UPDATE SET is_active = TRUE, joined_at = CURRENT_TIMESTAMP
        """)
        conn.execute(query, {"gid": group_id, "uid": target_user_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def remove_member(group_id, target_user_id, requester_email):
    conn = get_connection()
    try:
        req_id = get_user_id_by_email(conn, requester_email)
        check_permission(conn, group_id, req_id, ['owner', 'admin'])

        query = text("UPDATE Group_Members SET is_active = FALSE WHERE group_id = :gid AND user_id = :uid")
        conn.execute(query, {"gid": group_id, "uid": target_user_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def list_members(group_id, email):
    conn = get_connection()
    try:
        user_id = get_user_id_by_email(conn, email)
        check_permission(conn, group_id, user_id, ['owner', 'admin', 'member'])

        query = text("""
            SELECT u.id, u.first_name, u.last_name, u.email, u.picture_url, gm.role
            FROM Group_Members gm
            JOIN Users u ON gm.user_id = u.id
            WHERE gm.group_id = :gid AND gm.is_active = TRUE
        """)
        result = conn.execute(query, {"gid": group_id}).fetchall()
        
        members = []
        for row in result:
            members.append({
                "user_id": str(row[0]),
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "picture_url": row[4],
                "role": row[5]
            })
        return members
    except Exception as e:
        print(f"List members error: {e}")
        raise e

def assign_role(group_id, target_user_id, new_role, requester_email):
    conn = get_connection()
    try:
        req_id = get_user_id_by_email(conn, requester_email)
        my_role = check_permission(conn, group_id, req_id, ['owner', 'admin'])
        
        if my_role == 'admin' and new_role in ['admin', 'owner']:
             raise Exception("Admins cannot promote to admin/owner")

        conn.execute(text("""
            UPDATE Group_Members SET role = :role 
            WHERE group_id = :gid AND user_id = :uid
        """), {"role": new_role, "gid": group_id, "uid": target_user_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def leave_group(group_id, email):
    conn = get_connection()
    try:
        user_id = get_user_id_by_email(conn, email)
        role = check_permission(conn, group_id, user_id, ['owner', 'admin', 'member'])
        
        if role == 'owner':
            raise Exception("Owner cannot leave group. Delete the group or transfer ownership.")

        conn.execute(text("""
            UPDATE Group_Members SET is_active = FALSE 
            WHERE group_id = :gid AND user_id = :uid
        """), {"gid": group_id, "uid": user_id})
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e

def get_user_groups(email):
    conn = get_connection()
    try:
        user_id = get_user_id_by_email(conn, email)
        query = text("""
            SELECT g.id, g.name, g.description, g.picture_url, gm.role
            FROM Groups g
            JOIN Group_Members gm ON g.id = gm.group_id
            WHERE gm.user_id = :uid AND gm.is_active = TRUE AND g.is_deleted = FALSE
        """)
        result = conn.execute(query, {"uid": user_id}).fetchall()
        
        groups = []
        for row in result:
            groups.append({
                "id": str(row[0]),
                "name": row[1],
                "description": row[2],
                "picture_url": row[3],
                "role": row[4]
            })
        return groups
    except Exception as e:
        print(f"Get user groups error: {e}")
        return []

def update_group(group_id: str, data: dict):
    conn = get_connection()
    try:
        query = text("""
            UPDATE Groups 
            SET name = :name, 
                description = :description, 
                picture_url = :picture_url 
            WHERE id = :id
        """)
        conn.execute(query, {
            "name": data['name'],
            "description": data['description'],
            "picture_url": data['picture_url'],
            "id": group_id
        })
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e    