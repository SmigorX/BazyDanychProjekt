from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Login: postgres, Hasło: postgres, Host: localhost, Port: 5432, Baza: project
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/project"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()