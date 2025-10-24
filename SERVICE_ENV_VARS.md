# 各服务环境变量需求对照表

**更新日期**: 2025-10-24

---

## 📋 所有服务的环境变量需求

| 环境变量 | Auth | User | Order | Payment | Review | Notification | 说明 |
|---------|------|------|-------|---------|--------|--------------|------|
| **DATABASE_URL** | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | MySQL 数据库连接 |
| **MONGODB_URL** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | MongoDB 连接 |
| **RABBITMQ_URL** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | RabbitMQ 消息队列 |
| **REDIS_URL** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | Redis 缓存 |
| **JWT_SECRET_KEY** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | JWT 密钥 |
| **LOCAL_RABBITMQ_URL** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | 本地 RabbitMQ |
| **DOCKER_RABBITMQ_URL** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | Docker RabbitMQ |
| **AUTH_SERVICE_URL** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | Auth 服务地址 |
| **USER_SERVICE_URL** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | User 服务地址 |
| **ORDER_SERVICE_URL** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | Order 服务地址 |
| **PAYMENT_SERVICE_URL** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | Payment 服务地址 |
| **REVIEW_SERVICE_URL** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | Review 服务地址 |

---

## 🎯 各服务必需变量详情

### Auth Service
```bash
DATABASE_URL=mysql+aiomysql://test:test@localhost:3306/test_db
JWT_SECRET_KEY=test-secret-key-for-ci
LOCAL_RABBITMQ_URL=amqp://guest:guest@localhost:5672/
DOCKER_RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

### User Service
```bash
MONGODB_URL=mongodb://test:test@localhost:27017/test_db
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
AUTH_SERVICE_URL=http://localhost:8000
```

### Order Service
```bash
DATABASE_URL=mysql+aiomysql://test:test@localhost:3306/test_db
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
AUTH_SERVICE_URL=http://localhost:8000
USER_SERVICE_URL=http://localhost:8002
```

### Payment Service
```bash
DATABASE_URL=mysql+aiomysql://test:test@localhost:3306/test_db
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
AUTH_SERVICE_URL=http://localhost:8000
USER_SERVICE_URL=http://localhost:8002
ORDER_SERVICE_URL=http://localhost:8003
```

### Review Service
```bash
MONGODB_URL=mongodb://test:test@localhost:27017/test_db
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
AUTH_SERVICE_URL=http://localhost:8000
ORDER_SERVICE_URL=http://localhost:8003
USER_SERVICE_URL=http://localhost:8002
```

### Notification Service
```bash
MONGODB_URL=mongodb://test:test@localhost:27017/test_db
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
AUTH_SERVICE_URL=http://localhost:8000
USER_SERVICE_URL=http://localhost:8002
ORDER_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
REVIEW_SERVICE_URL=http://localhost:8005
```

---

## 💡 CI 解决方案

### 策略：提供所有环境变量

在 CI 中为所有服务提供完整的环境变量集合，即使某些服务不需要某些变量：

```yaml
env:
  # Database URLs
  DATABASE_URL: "mysql+aiomysql://test:test@localhost:3306/test_db"
  MONGODB_URL: "mongodb://test:test@localhost:27017/test_db"
  
  # Message Queue & Cache
  RABBITMQ_URL: "amqp://guest:guest@localhost:5672/"
  REDIS_URL: "redis://localhost:6379/0"
  
  # Auth Service specific
  JWT_SECRET_KEY: "test-secret-key-for-ci"
  LOCAL_RABBITMQ_URL: "amqp://guest:guest@localhost:5672/"
  DOCKER_RABBITMQ_URL: "amqp://guest:guest@localhost:5672/"
  
  # Service URLs
  AUTH_SERVICE_URL: "http://localhost:8000"
  USER_SERVICE_URL: "http://localhost:8002"
  ORDER_SERVICE_URL: "http://localhost:8003"
  PAYMENT_SERVICE_URL: "http://localhost:8004"
  REVIEW_SERVICE_URL: "http://localhost:8005"
```

**优点**:
- ✅ 简单：一个配置适用所有服务
- ✅ 可维护：不需要为每个服务单独配置
- ✅ 安全：额外的环境变量不会影响服务

**缺点**:
- ⚠️ 有些变量对某些服务是多余的

---

## 🔍 为什么需要这么多环境变量？

### 1. 配置类在导入时初始化

```python
# config.py
class Settings(BaseSettings):
    DATABASE_URL: str  # 必需字段
    RABBITMQ_URL: str  # 必需字段
    # ...

settings = Settings()  # ⚠️ 模块导入时就会验证
```

### 2. 导入链触发验证

```python
# test_order_service.py
from order_service.services import CustomerOrderService
  ↓
from order_service.dao import OrderDAO
  ↓
from order_service.models import Order
  ↓
from order_service.core.database import Base
  ↓
from order_service.core.config import settings  # ⚠️ 这里需要环境变量
  ↓
Settings()  # 验证所有必需字段
```

### 3. 即使使用 Mock 也需要

单元测试中虽然使用 Mock，但：
- ❌ Mock 只在测试函数内生效
- ❌ 模块导入在测试函数之前
- ✅ 必须在导入前设置环境变量

---

## 🧪 本地测试验证

### 方法 1: 导出环境变量

```bash
# 设置所有环境变量
export DATABASE_URL="mysql+aiomysql://test:test@localhost:3306/test_db"
export MONGODB_URL="mongodb://test:test@localhost:27017/test_db"
export RABBITMQ_URL="amqp://guest:guest@localhost:5672/"
export REDIS_URL="redis://localhost:6379/0"
export JWT_SECRET_KEY="test-secret-key-for-ci"
export LOCAL_RABBITMQ_URL="amqp://guest:guest@localhost:5672/"
export DOCKER_RABBITMQ_URL="amqp://guest:guest@localhost:5672/"
export AUTH_SERVICE_URL="http://localhost:8000"
export USER_SERVICE_URL="http://localhost:8002"
export ORDER_SERVICE_URL="http://localhost:8003"
export PAYMENT_SERVICE_URL="http://localhost:8004"
export REVIEW_SERVICE_URL="http://localhost:8005"

# 运行测试
cd services/order-service
poetry run pytest src/order_service/tests/unit/ -v
```

### 方法 2: 使用 .env 文件

在每个服务目录创建 `.env.test`:

```bash
# .env.test
DATABASE_URL=mysql+aiomysql://test:test@localhost:3306/test_db
MONGODB_URL=mongodb://test:test@localhost:27017/test_db
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=test-secret-key-for-ci
LOCAL_RABBITMQ_URL=amqp://guest:guest@localhost:5672/
DOCKER_RABBITMQ_URL=amqp://guest:guest@localhost:5672/
AUTH_SERVICE_URL=http://localhost:8000
USER_SERVICE_URL=http://localhost:8002
ORDER_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
REVIEW_SERVICE_URL=http://localhost:8005
```

然后使用 `python-dotenv` 加载：

```bash
cd services/order-service
cp .env.test .env
poetry run pytest src/order_service/tests/unit/ -v
```

---

## 📊 环境变量统计

| 类型 | 数量 | 变量 |
|------|------|------|
| **数据库** | 2 | DATABASE_URL, MONGODB_URL |
| **消息队列** | 3 | RABBITMQ_URL, LOCAL_RABBITMQ_URL, DOCKER_RABBITMQ_URL |
| **缓存** | 1 | REDIS_URL |
| **安全** | 1 | JWT_SECRET_KEY |
| **服务URL** | 5 | AUTH/USER/ORDER/PAYMENT/REVIEW_SERVICE_URL |
| **总计** | **12** | |

---

## 🚀 推荐做法

### 开发环境
- 使用 `.env` 文件
- 每个服务有自己的配置

### CI 环境
- 使用 `env` 块统一配置
- 所有服务共享相同的测试环境变量

### 生产环境
- 使用环境变量或密钥管理服务
- 每个服务独立配置

---

**版本**: 1.0  
**最后更新**: 2025-10-24  
**状态**: ✅ 已验证所有服务
