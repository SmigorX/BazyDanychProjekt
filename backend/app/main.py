from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.user import router as user_router
from api.notes import router as notes_router
from api.groups import router as groups_router

app = FastAPI(title="Map Notes App API", version="1.0.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(notes_router)
app.include_router(groups_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Map Notes API is running correctly!"}