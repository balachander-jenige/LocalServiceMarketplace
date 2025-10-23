import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import admin_notification_api, customer_inbox_api, provider_inbox_api
from .core.config import settings
from .core.mongodb import close_mongo_connection, connect_to_mongo
from .core.redis_client import close_redis_connection, connect_to_redis
from .events.consumers.event_consumer import start_consuming
from .messaging.rabbitmq_client import rabbitmq_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时连接数据库和消息队列
    await connect_to_mongo()
    await connect_to_redis()
    await rabbitmq_client.connect()
    asyncio.create_task(start_consuming())

    yield

    # 关闭时清理资源
    await rabbitmq_client.close()
    await close_redis_connection()
    await close_mongo_connection()


app = FastAPI(title=settings.SERVICE_NAME, version="1.0.0", lifespan=lifespan)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(customer_inbox_api.router)
app.include_router(provider_inbox_api.router)
app.include_router(admin_notification_api.router)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}
