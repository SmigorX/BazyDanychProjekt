from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db, engine
import models

# To sprawia, że Python 'widzi' Twoje tabele
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Działa! Witaj w API notatek."}

@app.get("/db-test")
def test_db(db: Session = Depends(get_db)):
    try:
        # Proste zapytanie SQL: policz użytkowników
        result = db.execute(text("SELECT count(*) FROM users"))
        count = result.scalar()
        return {
            "status": "SUKCES! Połączono z bazą w Dockerze", 
            "users_count": count
        }
    except Exception as e:
        return {"status": "BŁĄD POŁĄCZENIA", "error": str(e)}