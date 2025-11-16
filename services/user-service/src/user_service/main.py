import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import admin_user_api, customer_profile_api, provider_profile_api
from .core.config import settings
from .core.mongodb import close_mongo_connection, connect_to_mongo
from .events.consumers.event_consumer import start_consuming
from .messaging.rabbitmq_client import rabbitmq_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application Lifecycle Management"""
    # 启动WhenConnection MongoDB.
    await connect_to_mongo()

    # Connect RabbitMQ AndStart Consuming Events
    await rabbitmq_client.connect()
    asyncio.create_task(start_consuming())

    yield

    # Clean up resources on shutdown
    await rabbitmq_client.close()
    await close_mongo_connection()


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
app.include_router(customer_profile_api.router)
app.include_router(provider_profile_api.router)
app.include_router(admin_user_api.router)


@app.get("/health")
async def health_check():
    """Health Check"""
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}
