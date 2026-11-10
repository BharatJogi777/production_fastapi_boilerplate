from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from pwdlib import PasswordHash
from app.core.config import get_settings

_password_hasher = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return _password_hasher.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return _password_hasher.verify(password, password_hash)

def create_access_token(subject: str) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    claims: dict[str, Any] = {"sub":subject,"iat":now,
        "exp":now + timedelta(minutes=settings.access_token_expire_minutes)}
    return jwt.encode(claims, settings.secret_key.get_secret_value(), algorithm="HS256")

def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key.get_secret_value(),
        algorithms=["HS256"], options={"require":["sub","iat","exp"]})
