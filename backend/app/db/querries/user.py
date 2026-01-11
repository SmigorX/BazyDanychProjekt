import uuid

from datamodels.jwt import TokenModel
from db.connection import get_connection
from schema.user import (
    GetUserDataSchema,
    NewUserSchema,
    UpdateUserPasswordSchema,
    UpdateUserSchema,
)
from sqlalchemy import text


def create_user(user_data: NewUserSchema):
    conn = get_connection()
    # Check if email already exists
    email_check_query = text(
        """
        SELECT COUNT(*) 
        FROM Users 
        WHERE email = :email
    """
    )
    email_check_result = conn.execute(email_check_query, {"email": user_data.email})
    email_count = email_check_result.scalar()
    if email_count > 0:
        raise Exception("Email already exists")

    try:
        # Step 1: Insert the password hash into the Passwords table
        password_query = text(
            """
            INSERT INTO Passwords (id, hash, algorithm)
            VALUES (:id, :hash, :algorithm)
            RETURNING id
        """
        )
        password_values = {
            "id": str(uuid.uuid4()),
            "hash": user_data.hash,
            "algorithm": "argon2",  # or the algorithm you're using
        }
        password_id = conn.execute(password_query, password_values).scalar()

        # Step 2: Insert the user into the Users table, referencing the password_id
        user_query = text(
            """
            INSERT INTO Users (id, email, first_name, last_name, password_id)
            VALUES (:id, :email, :first_name, :last_name, :password_id)
        """
        )
        user_values = {
            "id": str(uuid.uuid4()),
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "password_id": password_id,
        }
        conn.execute(user_query, user_values)

        conn.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        conn.rollback()
        print(f"Error creating user: {e}")
        raise


def get_user_password_hash(email: str) -> str:
    conn = get_connection()
    try:
        query = text(
            """
            SELECT p.hash
            FROM Users u
            JOIN Passwords p ON u.password_id = p.id
            WHERE u.email = :email
        """
        )
        result = conn.execute(query, {"email": email}).fetchone()
        if result:
            return result[0]
        else:
            raise Exception("User not found")
    except Exception as e:
        print(f"Error retrieving user password hash: {e}")
        raise


def get_user_token_data(email: str) -> TokenModel | None:
    conn = get_connection()
    try:
        query = text(
            """
            SELECT id, email, first_name, last_name, profile_picture_url
            FROM Users
            WHERE email = :email
            """
        )
        result = conn.execute(query, {"email": email}).fetchone()
        if result:
            profile_picture_url = result[4]
            if profile_picture_url is None:
                profile_picture_url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse4.mm.bing.net%2Fth%2Fid%2FOIP.fTV7RXSxmBRpPs5Saw7IPQHaHa%3Fpid%3DApi&f=1&ipt=5dbfa5c0155c13af5616c8842de5b6fea8f715fb0edb35d817058a065dc4b7f3"
            token_data = TokenModel(
                email=result[1],
                first_name=result[2],
                last_name=result[3],
                profile_picture_url=profile_picture_url,
            )
            return token_data
        else:
            return None
    except Exception as e:
        print(f"Error retrieving user by email: {e}")
        raise


def update_user_data(user_data: UpdateUserSchema):
    conn = get_connection()
    try:
        query = text(
            """
            UPDATE Users
            SET first_name = :first_name,
                last_name = :last_name,
                profile_picture_url = :profile_picture
                description = :description
            WHERE email = :email
            """
        )
        values = {
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "profile_picture": user_data.profile_picture,
            "description": user_data.description,
            "email": user_data.email,
        }
        conn.execute(query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error updating user data: {e}")
        raise


def update_user_password(user_data: UpdateUserPasswordSchema):
    conn = get_connection()
    try:
        password_id_query = text(
            """
            SELECT password_id
            FROM Users
            WHERE email = :email
            """
        )
        result = conn.execute(password_id_query, {"email": user_data.email}).fetchone()
        if not result:
            raise Exception("User not found")
        password_id = result[0]

        update_query = text(
            """
            UPDATE Passwords
            SET hash = :hash
            WHERE id = :password_id
            """
        )
        values = {
            "hash": user_data.hash,
            "password_id": password_id,
        }
        conn.execute(update_query, values)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error updating user password: {e}")
        raise


def get_user_data(userid: str) -> GetUserDataSchema | None:
    conn = get_connection()
    try:
        query = text(
            """
            SELECT id, email, first_name, last_name, profile_picture_url, description
            FROM Users
            WHERE id = :userid
            """
        )
        result = conn.execute(query, {"userid": userid}).fetchone()
        if result:
            user_data = GetUserDataSchema(
                email=result[1],
                first_name=result[2],
                last_name=result[3],
                profile_picture=result[4] if result[4] else "",
                description=result[5] if result[5] else "",
                id=result[0],
            )
            return user_data
        else:
            return None
    except Exception as e:
        print(f"Error retrieving user data: {e}")
        raise


def delete_user(userid: str):
    pass
