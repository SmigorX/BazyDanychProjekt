import os

from sqlalchemy import create_engine

_connection = None


def get_connection():
    global _connection
    if not _connection:
        try:
            connection_string = os.getenv("DATABASE_URL")

            if not connection_string:
                print("DATABASE_URL environment variable is not set.")
                exit(1)

            engine = create_engine(connection_string)
            _connection = engine.connect()
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            exit(1)
    return _connection
