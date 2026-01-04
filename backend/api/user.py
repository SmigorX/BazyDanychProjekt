from core.user import hash_password
from datamodels.user import NewUserModel
from db.querries.user import create_user
from fastapi import APIRouter, HTTPException
from schema.user import NewUserSchema

router = APIRouter()


@router.post("/users/create", tags=["users"])
def new_user(user_data: NewUserModel):
    hash = hash_password(user_data.password)
    new_user = NewUserSchema(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hash=hash,
    )
    try:
        create_user(new_user)
        return {"message": "User created successfully"}
    except Exception as e:
        print(f"new_user creation api error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
