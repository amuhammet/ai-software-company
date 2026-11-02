import hashlib
import os
import time
from typing import Any, Dict, Optional

try:
    import jwt
except ImportError:  # pragma: no cover
    jwt = None

from app.core.config import settings


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password


def create_access_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    if jwt is None:
        raise RuntimeError("PyJWT is required for token generation. Install it in requirements.txt.")

    payload = {
        "sub": subject,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> Dict[str, Any]:
    if jwt is None:
        raise RuntimeError("PyJWT is required for token decoding. Install it in requirements.txt.")
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])


def get_current_active_user() -> Dict[str, Any]:
    """Placeholder dependency to be wired into FastAPI auth later."""
    return {"user_id": "demo-user", "role": "admin"}


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_active_user",
]
