from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from server.config.database import engine
from server.users.auth import validate_jwt_secret
from server.users.handlers import users_router
from server.users.models import Base

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    validate_jwt_secret()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users_router)


def start_server() -> None:
    uvicorn.run(
        "server.main:app",
        port=8080,
        reload=True,
    )


if __name__ == "__main__":
    start_server()
