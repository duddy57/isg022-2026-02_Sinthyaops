from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from server.config.database import get_db
from server.users.auth import create_access_token, get_current_user_id
from server.users.schemas import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from server.users.services import UserService

users_router = APIRouter(tags=["Users"], prefix="/users")


def service(db: Session = Depends(get_db)) -> UserService:  # noqa: B008
    return UserService(db)


def current_user(current_user_id: int, db: Session) -> UserResponse:
    user = UserService(db).get_user(current_user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)


@users_router.post("/create", response_model=UserResponse, status_code=201)
def create_user(
    payload: UserCreate,
    users: UserService = Depends(service),  # noqa: B008
) -> UserResponse:
    try:
        return UserResponse.model_validate(
            users.create_user(payload.username, str(payload.email), payload.password)
        )
    except IntegrityError as exc:
        users.db.rollback()
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
        ) from exc


@users_router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    users: UserService = Depends(service),  # noqa: B008
) -> TokenResponse:
    user = users.login_user(str(payload.email), payload.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))


@users_router.get("/me", response_model=UserResponse)
def read_user(
    current: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),  # noqa: B008
) -> UserResponse:
    return current_user(current, db)


@users_router.patch("/me", response_model=UserResponse)
@users_router.put("/me", response_model=UserResponse)
def update_user(
    payload: UserUpdate,
    current: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),  # noqa: B008
) -> UserResponse:
    current_user(current, db)
    try:
        user = UserService(db).update_user(
            current, **payload.model_dump(exclude_unset=True)
        )
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.model_validate(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Username or email already exists"
        ) from exc


@users_router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    current: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),  # noqa: B008
) -> None:
    current_user(current, db)
    UserService(db).delete_user(current)
