from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from .core.config import settings
from .core.mongodb import connect_to_mongo, close_mongo_connection
from .core.redis_client import connect_to_redis, close_redis_connection
from .messaging.rabbitmq_client import rabbitmq_client
from .events.consumers.event_consumer import start_consuming
from .api import customer_inbox_api, provider_inbox_api

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

app = FastAPI(
    title=settings.SERVICE_NAME,
    version="1.0.0",
    lifespan=lifespan
)

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

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0"
    }