import datetime
from os import getenv
import jwt
from argon2 import PasswordHasher
from datamodels.jwt import TokenModel

def get_jwt_signature_key():
    global signature_key
    signature_key = getenv("JWT_SIGNATURE_KEY")
    if not signature_key:
        print("JWT_SIGNATURE_KEY environment variable is not set.")
        exit(1)
    return signature_key

def hash_password(password: str, username: str) -> str:
    ph = PasswordHasher()
    return ph.hash(password, salt=username.encode())

def generate_jwt_token(user_model: TokenModel) -> str:
    payload = {
        "sub": user_model.email,
        "id": user_model.id,
        "first_name": user_model.first_name,
        "last_name": user_model.last_name,
        "profile_picture_url": user_model.profile_picture_url,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12),
    }
    secret_key = get_jwt_signature_key()
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def verify_jwt_token(token: str) -> TokenModel | None:
    secret_key = get_jwt_signature_key()
    try:
        decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])
        payload = TokenModel(
            id=decoded_token.get("id", ""),
            email=decoded_token["sub"],
            first_name=decoded_token["first_name"],
            last_name=decoded_token["last_name"],
            profile_picture_url=decoded_token["profile_picture_url"],
        )
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None