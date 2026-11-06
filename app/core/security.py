from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import Header, HTTPException, status

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-key-change-me")
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salt = hashlib.sha256(os.urandom(32)).hexdigest()
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"pbkdf2_sha256$100000${salt}${derived.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt, digest = hashed_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        return derived.hex() == digest
    except (TypeError, ValueError, AttributeError):
        return False


def create_access_token(
    subject: str,
    extra_claims: Optional[Dict[str, Any]] = None,
    expires_minutes: int = 60 * 24,
) -> str:
    now = datetime.utcnow()
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def get_current_tenant(
    x_tenant_id: str = Header(default="org_default", description="Tenant organization ID"),
    authorization: str | None = Header(default=None, description="Bearer token optional stub"),
) -> str:
    """
    Validates and extracts the tenant ID from request headers.
    Supports X-Tenant-ID header for transition/demo mode, with hooks for future JWT validation.
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing tenant identification header (X-Tenant-ID)",
        )

    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        _ = decode_access_token(token)

    return x_tenant_id


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_tenant",
]
