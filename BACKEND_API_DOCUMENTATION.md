# 后端接口文档 (Backend API Documentation)

## 📋 文档说明

本文档为后端开发者提供完整的微服务架构说明、接口定义、数据库模型和系统设计说明。

**版本**: v1.0  
**最后更新**: 2025-10-17  
**架构模式**: 微服务架构 + 事件驱动  
**技术栈**: FastAPI + MySQL + MongoDB + Redis + RabbitMQ

---

## 🏗️ 系统架构

### 架构图

```
┌─────────────────────┐
│   Frontend (Vue3)   │
└──────────┬──────────┘
           │ HTTP/REST
           ▼
┌──────────────────────────────────┐
│   Gateway Service (8080)         │
│   - JWT 认证                     │
│   - 限流保护 (60次/分钟)         │
│   - 统一响应格式                 │
│   - 请求路由转发                 │
└──────────┬───────────────────────┘
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
┌─────────┐  ┌─────────────────────────────┐
│  MySQL  │  │    Backend Services         │
│ (8306)  │◄─┤                             │
└─────────┘  │  ┌────────────────────┐    │
             │  │ Auth Service 8000  │    │
┌─────────┐  │  └────────────────────┘    │
│ MongoDB │  │  ┌────────────────────┐    │
│ (27017) │◄─┤  │ User Service 8002  │    │
└─────────┘  │  └────────────────────┘    │
             │  ┌────────────────────┐    │
┌─────────┐  │  │ Order Service 8003 │    │
│  Redis  │◄─┤  └────────────────────┘    │
│ (6379)  │  │  ┌────────────────────┐    │
└─────────┘  │  │Payment Service 8004│    │
             │  └────────────────────┘    │
┌─────────┐  │  ┌────────────────────┐    │
│RabbitMQ │◄─┤  │Review Service 8005 │    │
│ (5672)  │  │  └────────────────────┘    │
└─────────┘  │  ┌────────────────────┐    │
             │  │Notification Svc8006│    │
             │  └────────────────────┘    │
             └─────────────────────────────┘
```

---

## 📊 服务列表

| 服务名称 | 端口 | 数据库 | 主要功能 |
|----------|------|--------|----------|
| Gateway Service | 8080 | - | 统一网关、JWT 认证、限流 |
| Auth Service | 8000 | MySQL | 用户注册、登录、认证 |
| User Service | 8002 | MySQL | 用户资料管理（Customer/Provider）|
| Order Service | 8003 | MySQL | 订单发布、接单、状态管理 |
| Payment Service | 8004 | MySQL | 充值、支付、余额管理 |
| Review Service | 8005 | MongoDB | 评价管理、评分统计 |
| Notification Service | 8006 | MongoDB | 通知推送、消息管理 |

---

## 🔧 Gateway Service (端口: 8080)

### 服务说明

Gateway Service 是系统的统一入口，负责：
1. **请求路由**: 将客户端请求转发到对应的后端服务
2. **JWT 认证**: 验证用户身份和权限
3. **限流保护**: 防止 API 滥用（60次/分钟/IP）
4. **统一响应格式**: 包装所有响应为标准格式
5. **错误处理**: 全局异常捕获和友好错误提示

### 技术栈

- **框架**: FastAPI 0.104.1
- **Python**: 3.13
- **依赖管理**: Poetry
- **HTTP 客户端**: httpx (异步)

### 核心组件

#### 1. 认证中间件 (middleware.py)

```python
# JWT 验证
async def verify_auth_token(credentials: HTTPAuthorizationCredentials):
    """验证 JWT Token"""
    token = credentials.credentials
    # 调用 Auth Service 验证 Token
    # 返回用户信息

# 限流中间件
async def apply_rate_limit():
    """IP 限流: 60 次/分钟"""
    # 使用内存存储请求计数
    # 超过限制返回 429
```

#### 2. HTTP 客户端 (base_client.py)

```python
class BaseClient:
    """基础 HTTP 客户端"""
    
    async def _make_request(
        self, 
        method: str, 
        path: str, 
        token: Optional[str] = None,
        json_data: Optional[Dict] = None
    ):
        """发送 HTTP 请求到后端服务"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # 使用 httpx 发送异步请求
        # 处理响应和错误
```

#### 3. 统一响应格式 (response_dto.py)

```python
class ApiResponse(BaseModel):
    success: bool
    data: Any
    message: str
    error: Optional[str] = None
```

### 路由映射

所有路由前缀: `/api/v1`

| Gateway 路由 | 后端服务 | 方法 |
|-------------|---------|------|
| `/auth/register` | Auth Service | POST |
| `/auth/login` | Auth Service | POST |
| `/auth/me` | Auth Service | GET |
| `/customer/profile` | User Service | POST/GET/PUT |
| `/provider/profile` | User Service | POST/GET/PUT |
| `/customer/orders/*` | Order Service | POST/GET |
| `/provider/orders/*` | Order Service | GET/POST |
| `/customer/payments/*` | Payment Service | POST |
| `/reviews/*` | Review Service | POST/GET |
| `/customer/inbox` | Notification Service | GET |
| `/provider/inbox` | Notification Service | GET |

### 配置文件 (.env)

```env
# Gateway Service Configuration
SERVICE_NAME=gateway-service
SERVICE_PORT=8080
SECRET_KEY=auth-service-secret-key-2025

# Backend Services URLs
AUTH_SERVICE_URL=http://localhost:8000
USER_SERVICE_URL=http://localhost:8002
ORDER_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
REVIEW_SERVICE_URL=http://localhost:8005
NOTIFICATION_SERVICE_URL=http://localhost:8006
```

---

## 🔐 Auth Service (端口: 8000)

### 服务说明

负责用户认证和授权，提供用户注册、登录和 JWT Token 管理。

### 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0 (异步)
- **密码加密**: bcrypt
- **JWT**: PyJWT

### 数据库表结构

#### users 表

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);
```

**字段说明**:
- `id`: 用户主键
- `username`: 用户名（唯一）
- `email`: 邮箱（唯一，用于登录）
- `password_hash`: bcrypt 加密的密码
- `role_id`: 角色 ID（1=Customer, 2=Provider）
- `is_active`: 账号是否激活

### API 端点

#### POST /auth/register

**功能**: 用户注册

**请求 DTO**:
```python
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_id: int
```

**响应 DTO**:
```python
class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str
```

**业务逻辑**:
1. 验证邮箱格式和唯一性
2. 验证用户名唯一性
3. 使用 bcrypt 加密密码
4. 创建用户记录
5. 发布 `user.registered` 事件到 RabbitMQ

---

#### POST /auth/login

**功能**: 用户登录

**请求 DTO**:
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

**响应 DTO**:
```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

**业务逻辑**:
1. 根据邮箱查询用户
2. 验证密码（bcrypt.checkpw）
3. 生成 JWT Token（有效期 30 分钟）
4. 返回 Token

**JWT Payload**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "role_id": 1,
  "exp": 1697564400
}
```

---

#### GET /users/me

**功能**: 获取当前用户信息

**认证**: 需要 JWT Token

**响应 DTO**:
```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role_id: int
```

**业务逻辑**:
1. 从 Token 中提取 user_id
2. 查询用户信息
3. 返回用户数据

---

### 事件发布

Auth Service 发布以下事件到 RabbitMQ:

| 事件名称 | 触发时机 | Payload |
|---------|---------|---------|
| `user.registered` | 用户注册成功 | `{user_id, username, email, role_id}` |

---

## 👤 User Service (端口: 8002)

### 服务说明

管理用户详细资料，支持客户（Customer）和服务商（Provider）两种角色的资料管理。

### 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0 (异步)

### 数据库表结构

#### customer_profiles 表

```sql
CREATE TABLE customer_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    location VARCHAR(50) DEFAULT 'NORTH',
    address VARCHAR(255),
    budget_preference DECIMAL(10, 2) DEFAULT 0.0,
    balance DECIMAL(10, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_location (location)
);
```

**字段说明**:
- `user_id`: 关联 users 表的外键
- `location`: 地区（NORTH/SOUTH/EAST/WEST/CENTRAL）
- `address`: 详细地址
- `budget_preference`: 预算偏好
- `balance`: 账户余额

---

#### provider_profiles 表

```sql
CREATE TABLE provider_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    skills JSON DEFAULT '[]',
    experience_years INT DEFAULT 0,
    hourly_rate DECIMAL(10, 2) DEFAULT 0.0,
    availability VARCHAR(255),
    portfolio JSON DEFAULT '[]',
    total_earnings DECIMAL(10, 2) DEFAULT 0.0,
    rating DECIMAL(3, 2) DEFAULT 0.0,
    total_reviews INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_rating (rating)
);
```

**字段说明**:
- `user_id`: 关联 users 表的外键
- `skills`: 技能列表（JSON 数组）
- `experience_years`: 从业年限
- `hourly_rate`: 时薪
- `availability`: 可用时间描述
- `portfolio`: 作品集链接（JSON 数组）
- `total_earnings`: 总收入
- `rating`: 平均评分（自动计算）
- `total_reviews`: 评价总数（自动计算）

### API 端点

#### Customer Profile API

**路由前缀**: `/customer/profile`

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/` | 创建客户资料 | ✅ |
| GET | `/me` | 获取当前客户资料 | ✅ |
| PUT | `/me` | 更新当前客户资料 | ✅ |

**业务逻辑**:
- 创建时检查 user_id 是否已存在资料
- 更新时只修改提供的字段
- 从 JWT Token 获取 user_id，无需前端传递

---

#### Provider Profile API

**路由前缀**: `/provider/profile`

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/` | 创建服务商资料 | ✅ |
| GET | `/me` | 获取当前服务商资料 | ✅ |
| PUT | `/me` | 更新当前服务商资料 | ✅ |

**特殊字段处理**:
- `rating` 和 `total_reviews`: 由 Review Service 通过事件更新
- `total_earnings`: 由 Payment Service 通过事件更新

---

### 事件消费

User Service 消费以下事件:

| 事件名称 | 来源服务 | 处理逻辑 |
|---------|---------|---------|
| `review.created` | Review Service | 更新 provider 评分和评价数 |
| `payment.completed` | Payment Service | 更新 customer 余额和 provider 收入 |

---

## 📦 Order Service (端口: 8003)

### 服务说明

管理订单生命周期，包括订单发布、接单、状态更新等功能。

### 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0 (异步)
- **消息队列**: RabbitMQ

### 数据库表结构

#### orders 表

```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    provider_id INT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    price DECIMAL(10, 2) NOT NULL,
    location VARCHAR(50) NOT NULL,
    address VARCHAR(255),
    payment_status VARCHAR(50) DEFAULT 'unpaid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (provider_id) REFERENCES users(id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_provider_id (provider_id),
    INDEX idx_status (status),
    INDEX idx_location (location)
);
```

**字段说明**:
- `customer_id`: 客户 ID（外键）
- `provider_id`: 服务商 ID（外键，接单后才有值）
- `title`: 订单标题
- `description`: 订单描述
- `status`: 订单状态
- `price`: 订单金额
- `location`: 服务地点
- `address`: 详细地址
- `payment_status`: 支付状态

**订单状态流转**:
```
pending → accepted → in_progress → completed → paid
                  ↘ cancelled
```

### API 端点

#### Customer Order API

**路由前缀**: `/customer/orders`

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/publish` | 发布订单 | ✅ |
| GET | `/my` | 获取进行中的订单 | ✅ |
| GET | `/history` | 获取订单历史 | ✅ |
| POST | `/cancel/{order_id}` | 取消订单 | ✅ |

**业务逻辑**:

**发布订单**:
1. 验证价格 > 0
2. 验证标题不为空
3. 创建订单记录（status = pending）
4. 发布 `order.published` 事件

**取消订单**:
1. 验证订单归属
2. 验证订单状态（只能取消 pending 状态）
3. 更新状态为 cancelled
4. 发布 `order.cancelled` 事件

---

#### Provider Order API

**路由前缀**: `/provider/orders`

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/available` | 获取可接单列表 | ✅ |
| POST | `/accept/{order_id}` | 接受订单 | ✅ |
| POST | `/status/{order_id}` | 更新订单状态 | ✅ |
| GET | `/history` | 获取订单历史 | ✅ |

**业务逻辑**:

**接受订单**:
1. 验证订单状态为 pending
2. 验证订单未被其他人接单
3. 设置 provider_id
4. 更新状态为 accepted
5. 发布 `order.accepted` 事件

**更新订单状态**:
1. 验证订单归属（provider_id）
2. 验证状态流转合法性
3. 更新订单状态
4. 发布 `order.status_updated` 事件

---

### 事件发布

| 事件名称 | 触发时机 | Payload |
|---------|---------|---------|
| `order.published` | 订单发布 | `{order_id, customer_id, title, price, location}` |
| `order.accepted` | 订单被接受 | `{order_id, customer_id, provider_id}` |
| `order.status_updated` | 状态更新 | `{order_id, status, customer_id, provider_id}` |
| `order.cancelled` | 订单取消 | `{order_id, customer_id}` |

### 事件消费

| 事件名称 | 来源服务 | 处理逻辑 |
|---------|---------|---------|
| `payment.completed` | Payment Service | 更新订单支付状态为 paid |

---

## 💰 Payment Service (端口: 8004)

### 服务说明

管理用户余额和订单支付，提供充值和支付功能。

### 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0 (异步)

### 数据库表结构

#### payments 表

```sql
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    provider_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'balance',
    status VARCHAR(50) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (provider_id) REFERENCES users(id),
    INDEX idx_order_id (order_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_provider_id (provider_id)
);
```

**字段说明**:
- `order_id`: 关联的订单 ID
- `customer_id`: 客户 ID
- `provider_id`: 服务商 ID
- `amount`: 支付金额
- `payment_method`: 支付方式（balance=余额支付）
- `status`: 支付状态（pending/completed/failed）
- `transaction_id`: 交易流水号

---

#### transactions 表

```sql
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    balance_before DECIMAL(10, 2) NOT NULL,
    balance_after DECIMAL(10, 2) NOT NULL,
    order_id INT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_transaction_type (transaction_type)
);
```

**字段说明**:
- `transaction_type`: 交易类型（recharge/payment/refund/earning）
- `balance_before`: 交易前余额
- `balance_after`: 交易后余额

### API 端点

**路由前缀**: `/customer/payments`

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/recharge` | 充值余额 | ✅ |
| POST | `/pay` | 支付订单 | ✅ |

**业务逻辑**:

**充值余额**:
1. 验证金额 > 0
2. 更新 customer_profiles.balance
3. 创建交易记录（type=recharge）
4. 返回新余额

**支付订单**:
1. 验证订单状态为 completed
2. 验证订单归属
3. 验证余额充足
4. 扣除客户余额
5. 增加服务商收入
6. 创建支付记录
7. 创建交易记录
8. 发布 `payment.completed` 事件

---

### 事件发布

| 事件名称 | 触发时机 | Payload |
|---------|---------|---------|
| `payment.completed` | 支付成功 | `{order_id, customer_id, provider_id, amount}` |

---

## ⭐ Review Service (端口: 8005)

### 服务说明

管理订单评价和服务商评分，使用 MongoDB 存储评价数据。

### 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MongoDB 6.0
- **ODM**: Motor (异步 MongoDB 驱动)

### 数据库结构

#### reviews 集合

```javascript
{
  "_id": ObjectId("..."),
  "order_id": 1,
  "customer_id": 1,
  "provider_id": 2,
  "stars": 5,
  "content": "服务非常好",
  "created_at": ISODate("2025-10-17T10:00:00Z")
}
```

**索引**:
```javascript
db.reviews.createIndex({ "order_id": 1 }, { unique: true })
db.reviews.createIndex({ "provider_id": 1 })
db.reviews.createIndex({ "customer_id": 1 })
```

### API 端点

**路由前缀**: `/reviews`

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/` | 创建评价 | ✅ |
| GET | `/provider/me/rating` | 获取我的评分 | ✅ Provider |
| GET | `/provider/me/reviews` | 获取我的评价列表 | ✅ Provider |
| GET | `/provider/{id}/rating` | 获取服务商评分 | ❌ 公开 |
| GET | `/provider/{id}` | 获取服务商评价 | ❌ 公开 |

**业务逻辑**:

**创建评价**:
1. 验证订单状态为 paid
2. 验证订单归属（customer_id）
3. 验证评分范围（1-5）
4. 检查是否已评价（order_id 唯一）
5. 创建评价记录
6. 计算服务商新的平均评分
7. 发布 `review.created` 事件

**计算评分**:
```python
# 聚合查询
pipeline = [
    {"$match": {"provider_id": provider_id}},
    {"$group": {
        "_id": "$provider_id",
        "average_rating": {"$avg": "$stars"},
        "total_reviews": {"$sum": 1}
    }}
]
```

---

### 事件发布

| 事件名称 | 触发时机 | Payload |
|---------|---------|---------|
| `review.created` | 创建评价 | `{order_id, customer_id, provider_id, stars, average_rating, total_reviews}` |

---

## 📬 Notification Service (端口: 8006)

### 服务说明

异步处理系统通知，监听其他服务的事件并生成通知消息。

### 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: MongoDB 6.0
- **ODM**: Motor
- **消息队列**: RabbitMQ

### 数据库结构

#### customer_notifications 集合

```javascript
{
  "_id": ObjectId("..."),
  "customer_id": 1,
  "order_id": 3,
  "message": "您的订单 #3 已被服务商接受",
  "created_at": ISODate("2025-10-17T12:00:00Z"),
  "is_read": false
}
```

**索引**:
```javascript
db.customer_notifications.createIndex({ "customer_id": 1 })
db.customer_notifications.createIndex({ "order_id": 1 })
```

---

#### provider_notifications 集合

```javascript
{
  "_id": ObjectId("..."),
  "provider_id": 2,
  "order_id": 3,
  "message": "您成功接受了订单 #3",
  "created_at": ISODate("2025-10-17T12:00:00Z"),
  "is_read": false
}
```

**索引**:
```javascript
db.provider_notifications.createIndex({ "provider_id": 1 })
db.provider_notifications.createIndex({ "order_id": 1 })
```

### API 端点

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/customer/inbox/` | 获取客户通知 | ✅ Customer |
| GET | `/provider/inbox/` | 获取服务商通知 | ✅ Provider |

**查询逻辑**:
- 按 `created_at` 降序排序
- 限制返回最近 100 条
- 返回未读数量

---

### 事件消费

Notification Service 消费所有业务事件并生成相应通知：

| 事件名称 | 通知对象 | 通知内容 |
|---------|---------|---------|
| `order.published` | Customer | "您的订单 #{order_id} 已发布" |
| `order.accepted` | Customer | "您的订单 #{order_id} 已被服务商接受" |
| `order.accepted` | Provider | "您成功接受了订单 #{order_id}" |
| `order.status_updated` | Customer/Provider | "订单 #{order_id} 状态已更新为 {status}" |
| `order.cancelled` | Customer | "订单 #{order_id} 已取消" |
| `payment.completed` | Customer | "订单 #{order_id} 支付成功" |
| `payment.completed` | Provider | "订单 #{order_id} 已收到付款" |
| `review.created` | Provider | "客户对订单 #{order_id} 进行了评价（{stars}星）" |

---

## 🔄 事件驱动架构

### RabbitMQ 配置

**Exchange**: `freelancer_events` (Topic Exchange)

**Routing Keys**:
- `order.*`: 订单相关事件
- `payment.*`: 支付相关事件
- `review.*`: 评价相关事件
- `user.*`: 用户相关事件

### 事件流转示例

#### 完整订单流程的事件序列

```
1. Customer 发布订单
   └─> Order Service 发布: order.published
       └─> Notification Service 创建通知

2. Provider 接受订单
   └─> Order Service 发布: order.accepted
       └─> Notification Service 创建通知（Customer + Provider）

3. Provider 更新状态为 completed
   └─> Order Service 发布: order.status_updated
       └─> Notification Service 创建通知

4. Customer 支付订单
   └─> Payment Service 发布: payment.completed
       ├─> Order Service 更新支付状态
       ├─> User Service 更新余额和收入
       └─> Notification Service 创建通知

5. Customer 创建评价
   └─> Review Service 发布: review.created
       ├─> User Service 更新 Provider 评分
       └─> Notification Service 创建通知
```

---

## 🗄️ 数据库设计

### MySQL 数据库关系图

```
┌─────────────┐
│    users    │
└──────┬──────┘
       │
       ├───────────────────┬─────────────────┐
       │                   │                 │
       ▼                   ▼                 ▼
┌──────────────┐   ┌──────────────┐   ┌─────────┐
│customer_     │   │provider_     │   │ orders  │
│profiles      │   │profiles      │   └────┬────┘
└──────────────┘   └──────────────┘        │
                                            ▼
                                     ┌──────────┐
                                     │ payments │
                                     └──────────┘
                                     ┌──────────────┐
                                     │ transactions │
                                     └──────────────┘
```

### MongoDB 集合关系

```
reviews (按 provider_id 分组统计)
  ↓
customer_notifications (按 customer_id 查询)
  ↓
provider_notifications (按 provider_id 查询)
```

---

## 🔐 安全设计

### JWT Token 机制

**生成**:
```python
payload = {
    "user_id": user.id,
    "email": user.email,
    "role_id": user.role_id,
    "exp": datetime.utcnow() + timedelta(minutes=30)
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

**验证**:
```python
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
user_id = payload.get("user_id")
```

### 密码加密

使用 bcrypt 进行密码加密：
```python
# 加密
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# 验证
bcrypt.checkpw(password.encode(), password_hash)
```

### 权限控制

- **Gateway 层**: 验证 Token 有效性
- **Service 层**: 验证用户角色和资源归属
- **数据库层**: 外键约束保证数据一致性

---

## 📝 开发规范

### 代码结构

每个微服务遵循相同的目录结构：

```
service-name/
├── src/
│   └── service_name/
│       ├── __init__.py
│       ├── main.py           # FastAPI 应用入口
│       ├── api/              # API 路由层
│       │   ├── __init__.py
│       │   └── *_api.py
│       ├── core/             # 核心配置
│       │   ├── config.py     # 环境配置
│       │   ├── database.py   # 数据库连接
│       │   └── dependencies.py
│       ├── dao/              # 数据访问层
│       ├── domain/           # 领域模型
│       ├── dto/              # 数据传输对象
│       ├── events/           # 事件处理
│       │   ├── publishers/   # 事件发布
│       │   └── consumers/    # 事件消费
│       ├── messaging/        # RabbitMQ 客户端
│       ├── models/           # 数据库模型
│       ├── services/         # 业务逻辑层
│       └── tests/            # 单元测试
├── alembic/                  # 数据库迁移（MySQL 服务）
├── .env                      # 环境变量
├── pyproject.toml            # Poetry 依赖
└── README.md
```

### 命名规范

- **文件名**: 小写下划线（snake_case）
- **类名**: 大驼峰（PascalCase）
- **函数名**: 小写下划线（snake_case）
- **常量**: 大写下划线（UPPER_SNAKE_CASE）
- **DTO 类**: 以 Request/Response/DTO 结尾
- **API 路由文件**: 以 _api.py 结尾

### 异步编程

所有服务使用异步编程：
```python
# 数据库操作
async with AsyncSession() as session:
    result = await session.execute(query)

# HTTP 请求
async with httpx.AsyncClient() as client:
    response = await client.post(url, json=data)

# RabbitMQ 操作
await channel.default_exchange.publish(message, routing_key)
```

---

## 🧪 测试指南

### 单元测试

使用 pytest + pytest-asyncio：

```python
@pytest.mark.asyncio
async def test_create_order():
    """测试创建订单"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/customer/orders/publish",
            json={"title": "Test", "price": 100},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
```

### 集成测试

1. 启动所有服务和基础设施
2. 使用 Postman 或脚本测试完整业务流程
3. 验证事件传递和数据一致性

### 测试数据

使用 Docker Compose 的测试环境：
```bash
docker-compose -f docker-compose.test.yml up
pytest tests/
```

---

## 🚀 部署指南

### Docker 部署

每个服务的 Dockerfile：

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装 Poetry
RUN pip install poetry

# 复制依赖文件
COPY pyproject.toml poetry.lock ./

# 安装依赖
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# 复制代码
COPY src/ ./src/

# 启动服务
CMD ["uvicorn", "service_name.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes 部署

使用 Helm Chart 管理微服务部署：

```yaml
# values.yaml
services:
  auth:
    image: auth-service:latest
    port: 8000
    replicas: 3
  user:
    image: user-service:latest
    port: 8002
    replicas: 3
  # ... 其他服务
```

### 环境变量管理

使用 ConfigMap 和 Secret：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: service-config
data:
  DATABASE_HOST: mysql-service
  RABBITMQ_HOST: rabbitmq-service
---
apiVersion: v1
kind: Secret
metadata:
  name: service-secrets
type: Opaque
data:
  SECRET_KEY: <base64-encoded>
  DB_PASSWORD: <base64-encoded>
```

---

## 📊 监控和日志

### 日志格式

统一使用 JSON 格式日志：

```json
{
  "timestamp": "2025-10-17T10:00:00Z",
  "service": "order-service",
  "level": "INFO",
  "message": "Order created",
  "order_id": 123,
  "customer_id": 1,
  "trace_id": "abc-def-ghi"
}
```

### 监控指标

- **请求量**: 每秒请求数（RPS）
- **响应时间**: P50, P95, P99
- **错误率**: 4xx 和 5xx 错误比例
- **数据库连接池**: 活跃连接数
- **RabbitMQ**: 队列长度、消息速率
- **资源使用**: CPU、内存、磁盘

### 健康检查

每个服务提供 `/health` 端点：

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "order-service",
        "version": "1.0.0",
        "database": await check_database(),
        "rabbitmq": await check_rabbitmq()
    }
```

---

## 🔧 故障排查

### 常见问题

**1. 服务间调用超时**
- 检查网络连接
- 验证服务健康状态
- 查看 Gateway 日志

**2. 数据库连接池耗尽**
- 增加连接池大小
- 检查慢查询
- 优化数据库索引

**3. RabbitMQ 消息堆积**
- 增加消费者数量
- 优化事件处理逻辑
- 检查死信队列

**4. JWT Token 验证失败**
- 检查 SECRET_KEY 配置
- 验证 Token 是否过期
- 确认时钟同步

---

## 📚 API 文档生成

每个服务自动生成 OpenAPI 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 🔄 版本管理

### 数据库迁移

使用 Alembic 管理 MySQL 数据库版本：

```bash
# 创建迁移
alembic revision --autogenerate -m "Add new column"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### API 版本控制

使用 URL 路径版本：
- v1: `/api/v1/*`
- v2: `/api/v2/*` (未来版本)

---

## 📞 技术支持

**文档版本**: v1.0  
**最后更新**: 2025-10-17  
**维护团队**: Backend Development Team

如有技术问题，请查阅各服务的 README.md 或联系开发团队。
