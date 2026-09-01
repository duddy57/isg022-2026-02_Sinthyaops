"""Focused API tests using an in-memory SQLite database."""

# TestClient's dynamically typed compatibility layer has no useful strict stubs.
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

import os
from collections.abc import Generator

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-that-is-at-least-32-bytes")
os.environ.setdefault("APP_ENV", "development")

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from server.config.database import get_db
from server.main import app
from server.users.auth import validate_jwt_secret
from server.users.models import Base
from server.users.schemas import UserCreate


@pytest.fixture()
def client() -> Generator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    def override_db() -> Generator[Session]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_login_and_protected_crud(client: TestClient) -> None:
    created = client.post(
        "/users/create",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "password123",
        },
    )
    assert created.status_code == 201
    user_id = created.json()["id"]

    login = client.post(
        "/users/login",
        json={"email": "alice@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/users/me", headers=headers).status_code == 200
    updated = client.patch("/users/me", headers=headers, json={"username": "alice-new"})
    assert updated.status_code == 200
    assert updated.json()["username"] == "alice-new"
    assert client.delete("/users/me", headers=headers).status_code == 204
    assert client.get(f"/users/{user_id}", headers=headers).status_code == 404


def test_auth_and_duplicate_errors(client: TestClient) -> None:
    assert client.get("/users/me").status_code == 401
    payload = {"username": "bob", "email": "bob@example.com", "password": "password123"}
    assert client.post("/users/create", json=payload).status_code == 201
    assert client.post("/users/create", json=payload).status_code == 409
    assert (
        client.post(
            "/users/login", json={"email": payload["email"], "password": "wrongpass"}
        ).status_code
        == 401
    )


def test_password_byte_limit_and_long_email() -> None:
    with pytest.raises(ValidationError):
        UserCreate(
            username="long-password",
            email="long@example.com",
            password="é" * 40,
        )
    address = f"{'a' * 240}@x.com"
    user = UserCreate(
        username="long-email",
        email=address,
        password="password123",  # noqa: S106
    )
    assert str(user.email) == address


def test_jwt_secret_rejects_weak_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "short")
    with pytest.raises(RuntimeError, match="32 UTF-8 bytes"):
        validate_jwt_secret()
    monkeypatch.setenv("JWT_SECRET_KEY", "replace-with-a-long-random-secret")
    with pytest.raises(RuntimeError, match="non-placeholder"):
        validate_jwt_secret()
