from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import admin_user_api, auth_api, user_api
from .core.config import settings
from .core.database import Base, engine
from .messaging.rabbitmq_client import rabbitmq_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application Lifecycle Management"""
    # Create database tables on startup.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Connect RabbitMQ
    await rabbitmq_client.connect()

    yield

    # Clean up resources on shutdown
    await rabbitmq_client.close()
    await engine.dispose()


app = FastAPI(title=settings.SERVICE_NAME, version="1.0.0", lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(auth_api.router)
app.include_router(user_api.router)
app.include_router(admin_user_api.router)


@app.get("/health")
async def health_check():
    """Health Check"""
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}
