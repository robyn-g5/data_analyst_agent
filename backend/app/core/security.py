from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.supabase_client import get_service_client

_bearer = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    id: str
    email: str | None


def verify_token(credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> CurrentUser:
    """Verifies the bearer token by asking Supabase Auth directly, rather than
    decoding it locally. Avoids depending on a static JWT secret, which isn't
    guaranteed to exist/apply the same way across Supabase's legacy vs newer
    API key systems.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    client = get_service_client()
    try:
        response = client.auth.get_user(credentials.credentials)
    except Exception as exc:  # supabase-py raises AuthApiError for invalid/expired tokens
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
    user = response.user if response else None
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return CurrentUser(id=user.id, email=user.email)
