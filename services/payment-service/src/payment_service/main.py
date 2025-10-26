import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import payment_api
from .core.config import settings
from .core.database import Base, engine
from .events.consumers.event_consumer import start_consuming
from .messaging.rabbitmq_client import rabbitmq_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 连接 RabbitMQ 并开始消费事件
    await rabbitmq_client.connect()
    asyncio.create_task(start_consuming())

    yield

    # 关闭时清理资源
    await rabbitmq_client.close()
    await engine.dispose()


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
app.include_router(payment_api.router)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}
