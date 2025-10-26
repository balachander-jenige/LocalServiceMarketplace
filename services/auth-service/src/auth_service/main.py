from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import admin_user_api, auth_api, user_api
from .core.config import settings
from .core.database import Base, engine
from .messaging.rabbitmq_client import rabbitmq_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 连接 RabbitMQ
    await rabbitmq_client.connect()

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
app.include_router(auth_api.router)
app.include_router(user_api.router)
app.include_router(admin_user_api.router)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.SERVICE_NAME, "version": "1.0.0"}
