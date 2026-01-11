import uvicorn
from api.groups import router as groups_router
from api.notes import router as notes_router
from api.tags import router as tags_router
from api.user import router as user_router
from db.connection import get_connection
from fastapi import FastAPI

app = FastAPI()
app.include_router(user_router)
app.include_router(groups_router)
app.include_router(notes_router)
app.include_router(tags_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
