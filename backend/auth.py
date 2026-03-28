"""JWT PIN authentication."""

import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request
import jwt

JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
MANAGER_PIN = os.environ.get("MANAGER_PIN", "1234")
CREW_PIN = os.environ.get("CREW_PIN", "0000")


def create_token(role: str) -> str:
    payload = {
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(days=90),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_pin(pin: str) -> str | None:
    if pin == MANAGER_PIN:
        return "manager"
    if pin == CREW_PIN:
        return "crew"
    return None


def get_current_role(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("role", "crew")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_manager(role: str = Depends(get_current_role)) -> str:
    if role != "manager":
        raise HTTPException(status_code=403, detail="Manager access required")
    return role
