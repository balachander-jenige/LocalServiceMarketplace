import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import review_api
from .core.config import settings
from .core.mongodb import close_mongo_connection, connect_to_mongo
from .events.consumers.event_consumer import start_consuming
from .messaging.rabbitmq_client import rabbitmq_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await rabbitmq_client.connect()
    asyncio.create_task(start_consuming())
    yield
    await rabbitmq_client.close()
    await close_mongo_connection()


app = FastAPI(title=settings.SERVICE_NAME, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review_api.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}
