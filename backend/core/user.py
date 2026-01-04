from argon2 import PasswordHasher


def hash_password(password: str) -> str:
    ph = PasswordHasher()
    return ph.hash(password)
