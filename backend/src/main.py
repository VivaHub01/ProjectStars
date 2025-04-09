from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.db.database import get_async_session
from src.auth.admin.routes import admin_router
from src.auth.routes import auth_router
from src.user.routes import user_router
from src.accelerator.routes import accelerator_router
from src.core.openapi_config import setup_openapi_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f'server is starting ...')
    async for session in get_async_session():
        yield
    print(f'server is stopped')

app = FastAPI(lifespan=lifespan)


app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(accelerator_router)


setup_openapi_config(app)