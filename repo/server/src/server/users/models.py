from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    created_on: Mapped[datetime] = mapped_column(DateTime(), default=datetime.now)
    updated_on: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.now, onupdate=datetime.now
    )
