import os

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

_engine = None


def get_engine():
    global _engine
    if not _engine:
        try:
            connection_string = os.getenv("DATABASE_URL")

            if not connection_string:
                print("DATABASE_URL environment variable is not set.")
                exit(1)

            _engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True
            )
        except Exception as e:
            print(f"Error creating database engine: {e}")
            exit(1)
    return _engine


def get_connection():
    """Get a new connection from the pool for each request"""
    engine = get_engine()
    return engine.connect()
