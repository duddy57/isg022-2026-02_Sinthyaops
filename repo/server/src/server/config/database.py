import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_REQUIRED_ERROR = "DATABASE_URL is required outside APP_ENV=development"

app_env = os.getenv("APP_ENV", "").lower()
database_url = os.getenv("DATABASE_URL")
if not database_url:
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    if db_name and db_user and db_password:
        database_url = URL.create(
            drivername="postgresql+psycopg2",
            username=db_user,
            password=db_password,
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5433")),
            database=db_name,
        )
    elif app_env == "development":
        database_url = "sqlite:///./server.db"
    else:
        raise RuntimeError(DATABASE_REQUIRED_ERROR)

drivername = database_url.drivername if isinstance(database_url, URL) else database_url
connect_args = {"check_same_thread": False} if drivername.startswith("sqlite") else {}
engine = create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
