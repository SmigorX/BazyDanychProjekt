from core.user import generate_jwt_token, hash_password, verify_jwt_token
from datamodels.jwt import TokenModel
from datamodels.user import (
    DeleteUserModel,
    LoginUserModel,
    NewUserModel,
    UpdateUserModel,
    UpdateUserPasswordModel,
)
from db.querries.user import (
    create_user,
    delete_user,
    get_user_data,
    get_user_password_hash,
    get_user_token_data,
    update_user_data,
    update_user_password,
    update_user_email,
)
from fastapi import APIRouter, HTTPException
from schema.user import (
    GetUserDataSchema,
    LoginUserSchema,
    NewUserSchema,
    UpdateUserPasswordSchema,
    UpdateUserSchema,
)

router = APIRouter()


@router.post("/api/v1/users/create", tags=["users"])
def new_user(user_data: NewUserModel):
    hash = hash_password(user_data.password, user_data.email)
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


@router.post("/api/v1/users/login", tags=["users"])
def login_user(user_data: LoginUserModel):
    login_hash = hash_password(user_data.password, user_data.email)
    user = LoginUserSchema(
        email=user_data.email,
        hash=login_hash,
    )

    stored_hash = get_user_password_hash(user_data.email)
    if stored_hash is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.hash == stored_hash:
        token_data = get_user_token_data(user_data.email)
        if token_data:
            token = generate_jwt_token(token_data)
            return {"access_token": token, "token_type": "bearer"}

    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/api/v1/users/update/data", tags=["users"])
def update_user_profile_data(user_data: UpdateUserModel):
    token = verify_jwt_token(user_data.jwt)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if token.email != user_data.email:
        raise HTTPException(status_code=403, detail="Token does not match user email")
    
    updated_user = UpdateUserSchema(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        profile_picture=user_data.profile_picture,
        description=user_data.description,
    )
    try:
        update_user_data(updated_user)
        
        new_token_data = TokenModel(
            id=token.id, # <--- TUTAJ BRAKOWAŁO ID
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            profile_picture_url=user_data.profile_picture,
        )
        new_token = generate_jwt_token(new_token_data)
        return {
            "message": "User data updated successfully",
            "access_token": new_token,
            "token_type": "bearer",
        }
    except Exception as e:
        print(f"update_user_profile_data api error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/v1/users/update/password", tags=["users"])
def update_user_password_data(user_data: UpdateUserPasswordModel):
    token = verify_jwt_token(user_data.jwt)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if token.email != user_data.email:
        raise HTTPException(status_code=403, detail="Token does not match user")

    stored_hash = get_user_password_hash(user_data.email)
    if stored_hash is None:
        raise HTTPException(status_code=404, detail="User not found")

    old_password_hash = hash_password(user_data.old_password, user_data.email)
    if old_password_hash != stored_hash:
        raise HTTPException(status_code=401, detail="Old password is incorrect")

    new_password_hash = hash_password(user_data.new_password, user_data.email)
    try:
        updated_password_data = UpdateUserPasswordSchema(
            email=user_data.email,
            hash=new_password_hash,
        )
        update_user_password(updated_password_data)
        return {"message": "User password updated successfully"}
    except Exception as e:
        print(f"update_user_password api error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/api/v1/users/{userid}", tags=["users"])
def get_user_data_api(userid: str):
    try:
        user_data = get_user_data(userid)
        if user_data is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user_data
    except Exception as e:
        print(f"get_user_data api error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/api/v1/users/{userid}", tags=["users"])
def delete_user_api(userid: str, body: DeleteUserModel):
    token = verify_jwt_token(body.jwt)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if token.email != userid:
        raise HTTPException(status_code=403, detail="Token does not match user")

    stored_hash = get_user_password_hash(userid)
    if stored_hash is None:
        raise HTTPException(status_code=404, detail="User not found")

    password_hash = hash_password(body.password, userid)
    if password_hash != stored_hash:
        raise HTTPException(status_code=401, detail="Password is incorrect")

    try:
        delete_user(userid)
        return {"message": "User deleted successfully"}
    except Exception as e:
        print(f"delete_user api error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/api/v1/users/update/email", tags=["users"])
def update_email_api(body: dict):
    token = verify_jwt_token(body.get("jwt"))
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    email = token.email
    new_email = body.get("new_email")
    password = body.get("password")

    stored_hash = get_user_password_hash(email)
    if stored_hash is None:
        raise HTTPException(status_code=404, detail="User not found")

    password_hash = hash_password(password, email)
    if password_hash != stored_hash:
        raise HTTPException(status_code=401, detail="Błędne hasło")

    try:
        update_user_email({"old_email": email, "new_email": new_email})
        token_data = get_user_token_data(new_email)
        new_token = generate_jwt_token(token_data)
        return {"access_token": new_token, "message": "Email zaktualizowany"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))    