import uvicorn
from api.user import router as user_router
from db.connection import get_connection
from fastapi import FastAPI

app = FastAPI()
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
