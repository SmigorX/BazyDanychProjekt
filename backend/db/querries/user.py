import uuid

from db.connection import get_connection
from schema.user import NewUserSchema
from sqlalchemy import text


def create_user(user_data: NewUserSchema):
    conn = get_connection()
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
