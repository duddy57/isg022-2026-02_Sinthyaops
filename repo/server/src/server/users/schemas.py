from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

PASSWORD_LENGTH_ERROR = "Password must be at most 72 UTF-8 bytes"  # noqa: S105


def validate_password_length(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError(PASSWORD_LENGTH_ERROR)
    return password


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)

    _password_bytes = field_validator("password")(validate_password_length)


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)

    _password_bytes = field_validator("password")(validate_password_length)


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=254)
    password: str | None = Field(default=None, min_length=8, max_length=128)

    _password_bytes = field_validator("password")(validate_password_length)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"  # noqa: S105
