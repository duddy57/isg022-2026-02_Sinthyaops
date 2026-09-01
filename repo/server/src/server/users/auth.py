import os
from datetime import UTC, datetime, timedelta
from typing import Any, cast

import jwt  # type: ignore[import-not-found]
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
bearer = HTTPBearer(auto_error=False)
SECRET_PLACEHOLDER_ERROR = "JWT_SECRET_KEY must be configured and non-placeholder"  # noqa: S105
SECRET_LENGTH_ERROR = "JWT_SECRET_KEY must be at least 32 UTF-8 bytes"  # noqa: S105


def validate_jwt_secret() -> None:
    """Require an operator-provided signing key before the app accepts traffic."""
    secret = os.getenv("JWT_SECRET_KEY", "")
    rejected = {
        "",
        "secret",
        "change-me",
        "replace-with-a-long-random-secret",
        "generate-a-unique-32-byte-or-longer-value",
    }
    if secret.lower() in rejected or "placeholder" in secret.lower():
        raise RuntimeError(SECRET_PLACEHOLDER_ERROR)
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError(SECRET_LENGTH_ERROR)


def create_access_token(user_id: int) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode(  # type: ignore[no-any-return]
        {"sub": str(user_id), "exp": expires}, SECRET_KEY, algorithm=ALGORITHM
    )


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),  # noqa: B008
) -> int:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        decoded: Any = jwt.decode(  # type: ignore[no-untyped-call]
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        payload = cast("dict[str, object]", decoded)
        subject: object = payload.get("sub")
        if not isinstance(subject, str):
            raise unauthorized
        return int(subject)
    except (jwt.InvalidTokenError, ValueError, TypeError) as exc:  # type: ignore[attr-defined]
        raise unauthorized from exc
