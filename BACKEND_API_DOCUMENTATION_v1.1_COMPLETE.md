# 后端接口文档 (Backend API Documentation)

## 📋 文档说明

本文档为后端开发者提供完整的微服务架构说明、接口定义、数据库模型和系统设计说明。

**版本**: v1.1  
**最后更新**: 2025-10-22  
**架构模式**: 微服务架构 + 事件驱动  
**技术栈**: FastAPI + MySQL + MongoDB + Redis + RabbitMQ

> **重要提示**: 本文档适用于将微服务架构迁移到 Monolith 架构的参考文档

---

## 🏗️ 系统架构

### 微服务架构图

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
| Payment Service | 8004 | MySQL | 模拟支付、交易管理 |
| Review Service | 8005 | MongoDB | 评价管理、评分统计 |
| Notification Service | 8006 | MongoDB | 通知推送、消息管理 |

---

## 🔐 1. Auth Service (端口: 8000)

### 服务说明

负责用户认证和授权，提供用户注册、登录和 JWT Token 管理。

### 数据库表结构

#### users 表

```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    INDEX idx_email (email),
    INDEX idx_username (username)
);
```

**字段说明**:
- `id`: 用户主键（BIGINT）
- `username`: 用户名（VARCHAR(100)，唯一）
- `email`: 邮箱（VARCHAR(255)，唯一，用于登录）
- `password_hash`: bcrypt 加密的密码（VARCHAR(255)）
- `role_id`: 角色 ID（外键关联 roles 表）
- `created_at`: 创建时间
- `updated_at`: 更新时间

#### roles 表

```sql
CREATE TABLE roles (
    id INT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);
```

**角色数据**:
- `id=1`: Customer (客户)
- `id=2`: Provider (服务商)
- `id=3`: Admin (管理员)

### API 端点

#### POST /auth/register

**功能**: 用户注册

**请求**:
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role_id": 1
}
```

**响应**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com"
}
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

**请求**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
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
  "email": "john@example.com",
  "role_id": 1,
  "exp": 1697564400
}
```

---

#### GET /users/me

**功能**: 获取当前用户信息

**认证**: 需要 JWT Token

**响应**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role_id": 1
}
```

---

## 👤 2. User Service (端口: 8002)

### 服务说明

管理用户的个人资料信息，包括客户和服务商的详细信息。

### 数据库表结构

#### customer_profiles 集合 (MongoDB)

User Service 使用 MongoDB 存储客户资料。

```javascript
{
  "user_id": 1,
  "location": "NORTH",  // ENUM: NORTH, SOUTH, EAST, WEST, MID
  "address": "北京市朝阳区XX小区",
  "budget_preference": 1000.0,
  "created_at": ISODate("2025-10-22T10:00:00Z"),
  "updated_at": ISODate("2025-10-22T10:00:00Z")
}
```

**字段说明**:
- `user_id`: 用户 ID（关联 Auth Service 的 users 表）
- `location`: 所在区域（NORTH/SOUTH/EAST/WEST/MID）
- `address`: 详细地址（可选）
- `budget_preference`: 预算偏好（默认 0.0）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**索引**:
```javascript
db.customer_profiles.createIndex({ "user_id": 1 }, { unique: true })
```

---

#### provider_profiles 集合 (MongoDB)

```javascript
{
  "user_id": 2,
  "skills": ["Python", "FastAPI", "MongoDB"],
  "experience_years": 5,
  "hourly_rate": 50.0,
  "availability": "Full-time",
  "portfolio": ["https://example.com/project1", "https://example.com/project2"],
  "rating": 4.8,
  "total_reviews": 20,
  "created_at": ISODate("2025-10-22T10:00:00Z"),
  "updated_at": ISODate("2025-10-22T10:00:00Z")
}
```

**字段说明**:
- `user_id`: 用户 ID（关联 Auth Service 的 users 表）
- `skills`: 技能列表（数组）
- `experience_years`: 工作年限（默认 0）
- `hourly_rate`: 时薪（默认 0.0）
- `availability`: 可用性描述（可选）
- `portfolio`: 作品集 URLs（数组）
- `rating`: 平均评分（默认 5.0）
- `total_reviews`: 评价总数（默认 0）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**索引**:
```javascript
db.provider_profiles.createIndex({ "user_id": 1 }, { unique: true })
```

### API 端点

#### Customer Profile API

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/customer/profile` | 创建客户资料 | ✅ |
| GET | `/customer/profile` | 获取客户资料 | ✅ |
| PUT | `/customer/profile` | 更新客户资料 | ✅ |

#### Provider Profile API

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/provider/profile` | 创建服务商资料 | ✅ |
| GET | `/provider/profile` | 获取服务商资料 | ✅ |
| PUT | `/provider/profile` | 更新服务商资料 | ✅ |

**请求示例（Customer）**:
```json
{
  "location": "NORTH",
  "address": "北京市朝阳区XX小区",
  "budget_preference": 1000.0
}
```

**请求示例（Provider）**:
```json
{
  "skills": ["Python", "FastAPI", "MongoDB"],
  "experience_years": 5,
  "hourly_rate": 50.0,
  "availability": "Full-time",
  "portfolio": ["https://example.com/project1"]
}
```

---

## 📦 3. Order Service (端口: 8003) ⭐ 核心服务

### 服务说明

管理订单的完整生命周期，包括发布、审核、接单、状态更新等。

### 数据库表结构

#### orders 表

```sql
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    provider_id INT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    service_type ENUM('cleaning_repair', 'it_technology', 'education_training', 
                      'life_health', 'design_consulting', 'other') NOT NULL,
    status ENUM('pending_review', 'pending', 'accepted', 'in_progress', 
                'completed', 'cancelled', 'paid') DEFAULT 'pending_review',
    price DECIMAL(10, 2) NOT NULL,
    location ENUM('NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL') NOT NULL,
    address VARCHAR(500),
    service_start_time DATETIME,
    service_end_time DATETIME,
    payment_status ENUM('pending', 'paid') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (provider_id) REFERENCES users(id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_provider_id (provider_id),
    INDEX idx_status (status),
    INDEX idx_location (location),
    INDEX idx_service_type (service_type)
);
```

### 字段详解

| 字段名 | 类型 | 必填 | 说明 | v1.1 新增 |
|--------|------|------|------|-----------|
| id | INT | ✅ | 订单主键 | |
| customer_id | INT | ✅ | 客户 ID（外键） | |
| provider_id | INT | ❌ | 服务商 ID（接单后） | |
| title | VARCHAR(255) | ✅ | 订单标题 | |
| description | TEXT | ❌ | 订单描述 | |
| service_type | ENUM | ✅ | 服务类型 | ✅ |
| status | ENUM | ✅ | 订单状态 | ✅ pending_review |
| price | DECIMAL(10,2) | ✅ | 订单金额 | |
| location | ENUM | ✅ | 服务地点 | |
| address | VARCHAR(500) | ❌ | 详细地址 | |
| service_start_time | DATETIME | ❌ | 服务开始时间 | ✅ |
| service_end_time | DATETIME | ❌ | 服务结束时间 | ✅ |
| payment_status | ENUM | ✅ | 支付状态 | |
| created_at | DATETIME | ✅ | 创建时间 | |
| updated_at | DATETIME | ✅ | 更新时间 | |

### service_type 枚举值

| 枚举值 | 中文名称 |
|--------|---------|
| `cleaning_repair` | 清洁与维修 |
| `it_technology` | IT与技术 |
| `education_training` | 教育与培训 |
| `life_health` | 生活与健康 |
| `design_consulting` | 设计与咨询 |
| `other` | 其他服务 |

### 订单状态流转

```
pending_review → (admin approve) → pending → accepted → in_progress → completed → paid
             ↘ (admin reject) → cancelled
```

**状态说明**:
- `pending_review`: 待审核（订单发布后的初始状态）
- `pending`: 待接单（管理员审核通过）
- `accepted`: 已接单（服务商已接单）
- `in_progress`: 进行中（服务正在进行）
- `completed`: 已完成（服务已完成）
- `cancelled`: 已取消（客户取消或管理员拒绝）
- `paid`: 已支付（客户已支付订单）

---

### API 端点

#### 3.1 Customer Order API

**路由前缀**: `/customer/orders`

| 方法 | 路径 | 功能 | 认证 | 返回类型 |
|------|------|------|------|----------|
| POST | `/publish` | 发布订单 | ✅ | PublishOrderResponse |
| GET | `/my` | 获取进行中的订单 | ✅ | List[OrderDetail] |
| GET | `/my/{order_id}` | 获取订单详情 | ✅ | OrderDetail |
| GET | `/history` | 获取订单历史 | ✅ | List[OrderDetail] |
| POST | `/cancel/{order_id}` | 取消订单 | ✅ | CancelOrderResponse |

##### POST /customer/orders/publish

**功能**: 客户发布订单

**请求**:
```json
{
  "title": "需要维修电脑",
  "description": "笔记本电脑无法开机",
  "service_type": "it_technology",
  "price": 200.00,
  "location": "NORTH",
  "address": "北京市朝阳区XX小区",
  "service_start_time": "2025-10-25T09:00:00",
  "service_end_time": "2025-10-25T12:00:00"
}
```

**响应**:
```json
{
  "order_id": 1,
  "message": "订单发布成功，等待管理员审核"
}
```

**业务逻辑**:
1. 验证价格 > 0
2. 验证标题不为空
3. ✅ **v1.1**: 验证 service_type 有效性
4. ✅ **v1.1**: 验证服务时间范围（end > start）
5. ✅ **v1.1**: 创建订单记录（status = pending_review）
6. 发布 `order.published` 事件

---

##### GET /customer/orders/my

**功能**: 获取客户进行中的订单列表

**查询参数**: 无

**响应**: OrderDetail 数组（17个字段）

```json
[
  {
    "id": 1,
    "customer_id": 5,
    "provider_id": 2,
    "title": "需要维修电脑",
    "description": "笔记本电脑无法开机",
    "service_type": "it_technology",
    "status": "pending",
    "price": 200.00,
    "location": "NORTH",
    "address": "北京市朝阳区XX小区",
    "service_start_time": "2025-10-25T09:00:00",
    "service_end_time": "2025-10-25T12:00:00",
    "payment_status": "pending",
    "created_at": "2025-10-22T10:00:00",
    "updated_at": "2025-10-22T10:00:00"
  }
]
```

**业务逻辑**:
- 查询状态不为 completed, cancelled, paid 的订单
- ✅ **v1.1**: 返回完整 OrderDetail（17字段，之前只返回7字段）

---

##### GET /customer/orders/my/{order_id}

**功能**: 获取订单详情

**响应**: OrderDetail 对象（17个字段）

**业务逻辑**:
- 验证订单归属（customer_id）
- ✅ **v1.1**: 返回完整订单信息

---

##### GET /customer/orders/history

**功能**: 获取客户历史订单列表

**响应**: OrderDetail 数组（17个字段）

**业务逻辑**:
- 查询状态为 completed, cancelled, paid 的订单
- ✅ **v1.1**: 返回完整 OrderDetail（17字段）

---

##### POST /customer/orders/cancel/{order_id}

**功能**: 取消订单

**响应**:
```json
{
  "message": "订单已取消"
}
```

**业务逻辑**:
1. 验证订单归属
2. 验证订单状态（只能取消 pending/pending_review 状态）
3. 更新状态为 cancelled
4. 发布 `order.cancelled` 事件

---

#### 3.2 Provider Order API

**路由前缀**: `/provider/orders`

| 方法 | 路径 | 功能 | 认证 | 返回类型 |
|------|------|------|------|----------|
| GET | `/available` | 获取可接单列表 | ✅ | List[OrderDetail] |
| POST | `/accept/{order_id}` | 接受订单 | ✅ | AcceptOrderResponse |
| GET | `/my/{order_id}` | 获取订单详情 | ✅ | OrderDetail |
| POST | `/status/{order_id}` | 更新订单状态 | ✅ | UpdateStatusResponse |
| GET | `/history` | 获取订单历史 | ✅ | List[OrderDetail] |

##### GET /provider/orders/available

**功能**: 获取可接单列表

**响应**: OrderDetail 数组（17个字段）

**业务逻辑**:
- ✅ **v1.1**: 只显示状态为 pending 的订单（已通过管理员审核）
- ✅ **v1.1**: 返回完整 OrderDetail（17字段）

---

##### POST /provider/orders/accept/{order_id}

**功能**: 接受订单

**响应**:
```json
{
  "message": "成功接单"
}
```

**业务逻辑**:
1. 验证订单状态为 pending
2. 验证订单未被其他人接单
3. 设置 provider_id
4. 更新状态为 accepted
5. 发布 `order.accepted` 事件

---

##### GET /provider/orders/my/{order_id}

**功能**: 获取订单详情（✅ v1.1 新增）

**响应**: OrderDetail 对象（17个字段）

**业务逻辑**:
- 验证订单归属（provider_id）
- 返回完整订单信息

---

##### POST /provider/orders/status/{order_id}

**功能**: 更新订单状态

**请求**:
```json
{
  "status": "in_progress"
}
```

**业务逻辑**:
1. 验证订单归属（provider_id）
2. 验证状态流转合法性
3. 更新订单状态
4. 发布 `order.status_updated` 事件

---

##### GET /provider/orders/history

**功能**: 获取历史订单

**响应**: OrderDetail 数组（17个字段）

**业务逻辑**:
- ✅ **v1.1**: 返回完整 OrderDetail（17字段）

---

#### 3.3 Admin Order API (✅ v1.1 新增)

**路由前缀**: `/admin/orders`

| 方法 | 路径 | 功能 | 认证 | 返回类型 |
|------|------|------|------|----------|
| GET | `` | 获取所有订单 | ✅ Admin | List[OrderDetail] |
| GET | `/pending-review` | 获取待审核订单 | ✅ Admin | List[OrderDetail] |
| GET | `/{order_id}` | 获取订单详情 | ✅ Admin | OrderDetail |
| POST | `/{order_id}/approve` | 审批订单 | ✅ Admin | ApproveOrderResponse |
| PUT | `/{order_id}` | 更新订单信息 | ✅ Admin | OrderDetail |
| DELETE | `/{order_id}` | 删除订单 | ✅ Admin | DeleteOrderResponse |

##### GET /admin/orders

**功能**: 获取所有订单（支持状态过滤）

**查询参数**:
- `status` (可选): 过滤订单状态

**示例**:
```
GET /admin/orders?status=pending_review
```

**响应**: OrderDetail 数组（17个字段）

---

##### GET /admin/orders/pending-review

**功能**: 获取待审核订单列表

**响应**: OrderDetail 数组（17个字段）

**业务逻辑**:
- 只返回状态为 pending_review 的订单

---

##### GET /admin/orders/{order_id}

**功能**: 获取订单详情

**响应**: OrderDetail 对象（17个字段）

---

##### POST /admin/orders/{order_id}/approve

**功能**: 审批订单（批准或拒绝）

**请求**:
```json
{
  "approved": true,
  "reject_reason": "订单信息不完整"
}
```

**参数说明**:
- `approved`: true=批准, false=拒绝
- `reject_reason`: 拒绝原因（拒绝时必填）

**响应**:
```json
{
  "message": "订单已批准"
}
```

**业务逻辑**:

**批准订单** (`approved: true`):
1. 验证订单状态为 pending_review
2. 更新状态为 pending
3. 发布 `order.approved` 事件
4. 客户收到通知: "Your order #{order_id} has been approved by admin..."

**拒绝订单** (`approved: false`):
1. 验证订单状态为 pending_review
2. 验证 reject_reason 不为空
3. 更新状态为 cancelled
4. 发布 `order.rejected` 事件（包含拒绝原因）
5. 客户收到通知: "Your order #{order_id} has been rejected. Reason: {reason}"

---

##### PUT /admin/orders/{order_id}

**功能**: 更新订单信息

**请求**（支持部分更新）:
```json
{
  "title": "更新后的标题",
  "price": 250.00,
  "service_type": "cleaning_repair"
}
```

**响应**: 更新后的 OrderDetail 对象

---

##### DELETE /admin/orders/{order_id}

**功能**: 删除订单

**响应**:
```json
{
  "message": "订单已删除"
}
```

**注意**: 物理删除，建议只在测试环境使用

---

### OrderDetail 完整字段列表（17个字段）

```typescript
interface OrderDetail {
  id: number;                      // 订单 ID
  customer_id: number;             // 客户 ID
  provider_id: number | null;      // 服务商 ID
  title: string;                   // 订单标题
  description: string;             // 订单描述
  service_type: ServiceType;       // 服务类型 (v1.1)
  status: OrderStatus;             // 订单状态
  price: number;                   // 订单金额
  location: Location;              // 服务地点
  address: string;                 // 详细地址
  service_start_time: string;      // 服务开始时间 (v1.1)
  service_end_time: string;        // 服务结束时间 (v1.1)
  payment_status: PaymentStatus;   // 支付状态
  created_at: string;              // 创建时间
  updated_at: string;              // 更新时间
}
```

---

### 订单事件发布

| 事件名称 | 触发时机 | Payload |
|---------|---------|---------|
| `order.published` | 订单发布 | `{order_id, customer_id, title, price, location, service_type}` |
| `order.approved` | 管理员审核通过 (✅ v1.1) | `{order_id, customer_id}` |
| `order.rejected` | 管理员审核拒绝 (✅ v1.1) | `{order_id, customer_id, reject_reason}` |
| `order.accepted` | 订单被接受 | `{order_id, customer_id, provider_id}` |
| `order.status_updated` | 状态更新 | `{order_id, status, customer_id, provider_id}` |
| `order.cancelled` | 订单取消 | `{order_id, customer_id}` |

---

## 💰 4. Payment Service (端口: 8004)

### 服务说明

管理订单支付，提供模拟支付功能（v1.1 简化）。

### 数据库表结构

#### payments 表

```sql
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    customer_id INT NOT NULL,
    provider_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) DEFAULT 'simulated',
    status VARCHAR(50) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (provider_id) REFERENCES users(id),
    UNIQUE KEY unique_order_payment (order_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_provider_id (provider_id)
);
```

### API 端点

**路由前缀**: `/customer/payments`

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/pay` | 支付订单（模拟支付） | ✅ |

#### POST /customer/payments/pay

**功能**: 支付订单（✅ v1.1 简化为模拟支付）

**请求**:
```json
{
  "order_id": 1
}
```

**响应**:
```json
{
  "message": "支付成功",
  "transaction_id": "TXN20251022001"
}
```

**业务逻辑** (✅ v1.1 简化):
1. 验证订单状态为 completed
2. 验证订单归属
3. 模拟支付成功（无需实际资金）
4. 创建支付记录
5. 更新订单支付状态为 paid
6. 发布 `payment.completed` 事件

**v1.1 变更说明**:
- ❌ 移除充值功能（`POST /customer/payments/recharge`）
- ✅ 简化支付流程，无需余额验证
- ✅ 直接模拟支付成功

---

### 事件发布

| 事件名称 | 触发时机 | Payload |
|---------|---------|---------|
| `payment.completed` | 支付成功 | `{order_id, customer_id, provider_id, amount}` |

---

## ⭐ 5. Review Service (端口: 8005)

### 服务说明

管理订单评价和服务商评分，使用 MongoDB 存储评价数据。

### 数据库结构

#### reviews 集合 (MongoDB)

```javascript
{
  "_id": ObjectId("..."),
  "order_id": 1,
  "customer_id": 1,
  "provider_id": 2,
  "stars": 5,
  "content": "服务非常好",
  "created_at": ISODate("2025-10-22T10:00:00Z")
}
```

**索引**:
```javascript
db.reviews.createIndex({ "order_id": 1 }, { unique: true })
db.reviews.createIndex({ "provider_id": 1 })
db.reviews.createIndex({ "customer_id": 1 })
```

### API 端点

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| POST | `/reviews/create` | 创建评价 | ✅ Customer |
| GET | `/reviews/provider/{provider_id}` | 获取服务商评价列表 | ✅ |

#### POST /reviews/create

**功能**: 创建订单评价

**请求**:
```json
{
  "order_id": 1,
  "stars": 5,
  "content": "服务非常专业，态度很好"
}
```

**响应**:
```json
{
  "review_id": "507f1f77bcf86cd799439011",
  "message": "评价创建成功"
}
```

**业务逻辑**:
1. 验证订单状态为 paid
2. 验证订单归属（customer_id）
3. 验证评分范围（1-5星）
4. 验证订单未被评价
5. 创建评价记录
6. 发布 `review.created` 事件

---

#### GET /reviews/provider/{provider_id}

**功能**: 获取服务商的所有评价

**响应**:
```json
[
  {
    "review_id": "507f1f77bcf86cd799439011",
    "order_id": 1,
    "customer_id": 5,
    "stars": 5,
    "content": "服务非常专业",
    "created_at": "2025-10-22T10:00:00Z"
  }
]
```

---

### 事件发布

| 事件名称 | 触发时机 | Payload |
|---------|---------|---------|
| `review.created` | 评价创建 | `{order_id, provider_id, stars, customer_id}` |

---

## 🔔 6. Notification Service (端口: 8006)

### 服务说明

管理用户通知，消费业务事件并生成相应的通知消息。

### 数据库结构

#### notifications 集合 (MongoDB)

```javascript
{
  "_id": ObjectId("..."),
  "user_id": 1,
  "type": "order_update",
  "message": "您的订单 #123 已被接受",
  "is_read": false,
  "related_id": 123,
  "created_at": ISODate("2025-10-22T10:00:00Z")
}
```

**索引**:
```javascript
db.notifications.createIndex({ "user_id": 1, "created_at": -1 })
db.notifications.createIndex({ "is_read": 1 })
```

### API 端点

| 方法 | 路径 | 功能 | 认证 |
|------|------|------|------|
| GET | `/customer/inbox/` | 获取客户通知 | ✅ Customer |
| GET | `/provider/inbox/` | 获取服务商通知 | ✅ Provider |

**响应示例**:
```json
{
  "notifications": [
    {
      "id": "507f1f77bcf86cd799439011",
      "type": "order_update",
      "message": "您的订单 #123 已被接受",
      "is_read": false,
      "related_id": 123,
      "created_at": "2025-10-22T10:00:00Z"
    }
  ],
  "unread_count": 5
}
```

---

### 事件消费

Notification Service 消费所有业务事件并生成相应通知：

| 事件名称 | 通知对象 | 通知内容 |
|---------|---------|---------|
| `order.published` | Customer | "您的订单 #{order_id} 已发布，等待管理员审核" |
| `order.approved` | Customer | "Your order #{order_id} has been approved by admin..." (✅ v1.1) |
| `order.rejected` | Customer | "Your order #{order_id} has been rejected. Reason: {reason}" (✅ v1.1) |
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

### 完整订单流程事件序列（v1.1）

```
1. Customer 发布订单
   └─> Order Service 发布: order.published
       └─> Notification Service 创建通知（等待审核）

2. Admin 审核订单 (✅ v1.1 新增)
   ├─> 批准: Order Service 发布: order.approved
   │   └─> Notification Service 创建客户通知（审核通过）
   │
   └─> 拒绝: Order Service 发布: order.rejected
       └─> Notification Service 创建客户通知（审核拒绝+原因）

3. Provider 接受订单（仅限已批准的订单）
   └─> Order Service 发布: order.accepted
       └─> Notification Service 创建通知（Customer + Provider）

4. Provider 更新状态为 completed
   └─> Order Service 发布: order.status_updated
       └─> Notification Service 创建通知

5. Customer 支付订单（模拟支付 ✅ v1.1）
   └─> Payment Service 发布: payment.completed
       ├─> Order Service 更新支付状态
       └─> Notification Service 创建通知

6. Customer 创建评价
   └─> Review Service 发布: review.created
       ├─> User Service 更新 Provider 评分
       └─> Notification Service 创建通知
```

---

## 🗄️ 数据库设计

### 数据库架构概览

**MySQL 数据库** (Auth Service):
- `users` 表 - 用户账号信息
- `roles` 表 - 角色定义

**MySQL 数据库** (Order Service):
- `orders` 表 - 订单信息

**MySQL 数据库** (Payment Service):
- `payments` 表 - 支付记录

**MongoDB 数据库** (User Service):
- `customer_profiles` 集合 - 客户资料
- `provider_profiles` 集合 - 服务商资料

**MongoDB 数据库** (Review Service):
- `reviews` 集合 - 评价记录

**MongoDB 数据库** (Notification Service):
- `notifications` 集合 - 通知消息

### 数据关系图

```
Auth Service (MySQL)
┌─────────────┐
│    users    │ ←──────┐
│  (MySQL)    │        │
└──────┬──────┘        │
       │               │ user_id (关联)
       │               │
       ├───────────────┼──────────────────────┐
       │               │                      │
       ▼               ▼                      ▼
┌──────────────┐ ┌──────────────┐      ┌─────────┐
│customer_     │ │provider_     │      │ orders  │ (MySQL)
│profiles      │ │profiles      │      │ (MySQL) │
│ (MongoDB)    │ │ (MongoDB)    │      └────┬────┘
└──────────────┘ └──────────────┘           │
  User Service    User Service              │
                                            ▼
                                      ┌─────────┐
                                      │payments │ (MySQL)
                                      │ (MySQL) │
                                      └─────────┘
                                    Payment Service

独立 MongoDB 集合:
┌─────────────┐       ┌──────────────┐
│   reviews   │       │notifications │
│ (MongoDB)   │       │  (MongoDB)   │
└─────────────┘       └──────────────┘
Review Service        Notification Service
```

**说明**:
- `users` 表在 Auth Service 的 MySQL 中
- `customer_profiles` 和 `provider_profiles` 在 User Service 的 MongoDB 中，通过 `user_id` 关联 `users` 表
- `orders` 和 `payments` 在各自服务的 MySQL 中
- `reviews` 和 `notifications` 在各自服务的 MongoDB 中

---

## 🔌 Gateway Service 路由映射

### 路由前缀

所有路由前缀: `/api/v1`

### 完整路由映射表

| Gateway 路由 | 后端服务 | 端口 | 方法 | 功能 |
|-------------|---------|------|------|------|
| `/auth/register` | Auth Service | 8000 | POST | 用户注册 |
| `/auth/login` | Auth Service | 8000 | POST | 用户登录 |
| `/auth/me` | Auth Service | 8000 | GET | 获取当前用户 |
| `/customer/profile` | User Service | 8002 | POST/GET/PUT | 客户资料管理 |
| `/provider/profile` | User Service | 8002 | POST/GET/PUT | 服务商资料管理 |
| `/customer/orders/publish` | Order Service | 8003 | POST | 发布订单 |
| `/customer/orders/my` | Order Service | 8003 | GET | 客户进行中订单 |
| `/customer/orders/my/{order_id}` | Order Service | 8003 | GET | 客户订单详情 (✅ v1.1) |
| `/customer/orders/history` | Order Service | 8003 | GET | 客户历史订单 |
| `/customer/orders/cancel/{order_id}` | Order Service | 8003 | POST | 取消订单 |
| `/provider/orders/available` | Order Service | 8003 | GET | 可接单列表 |
| `/provider/orders/accept/{order_id}` | Order Service | 8003 | POST | 接受订单 |
| `/provider/orders/my/{order_id}` | Order Service | 8003 | GET | 服务商订单详情 (✅ v1.1) |
| `/provider/orders/status/{order_id}` | Order Service | 8003 | POST | 更新订单状态 |
| `/provider/orders/history` | Order Service | 8003 | GET | 服务商历史订单 |
| `/admin/orders` | Order Service | 8003 | GET | 所有订单 (✅ v1.1) |
| `/admin/orders/pending-review` | Order Service | 8003 | GET | 待审核订单 (✅ v1.1) |
| `/admin/orders/{order_id}` | Order Service | 8003 | GET | 订单详情 (✅ v1.1) |
| `/admin/orders/{order_id}/approve` | Order Service | 8003 | POST | 审批订单 (✅ v1.1) |
| `/admin/orders/{order_id}` | Order Service | 8003 | PUT | 更新订单 (✅ v1.1) |
| `/admin/orders/{order_id}` | Order Service | 8003 | DELETE | 删除订单 (✅ v1.1) |
| `/customer/payments/pay` | Payment Service | 8004 | POST | 支付订单 |
| `/reviews/create` | Review Service | 8005 | POST | 创建评价 |
| `/reviews/provider/{provider_id}` | Review Service | 8005 | GET | 服务商评价列表 |
| `/customer/inbox` | Notification Service | 8006 | GET | 客户通知 |
| `/provider/inbox` | Notification Service | 8006 | GET | 服务商通知 |

---

## 🔐 认证和授权

### JWT Token 机制

**生成**: Auth Service 在登录时生成

**验证**: Gateway Service 验证所有受保护的请求

**Token 结构**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "role_id": 1,
  "exp": 1697564400
}
```

**有效期**: 30 分钟

**Header 格式**:
```
Authorization: Bearer <token>
```

### 角色权限

| 角色 | role_id | 权限 |
|------|---------|------|
| Customer | 1 | 发布订单、查看自己的订单、支付、评价 |
| Provider | 2 | 查看可接单列表、接单、更新订单状态 |
| Admin | 3 | 审核订单、管理所有订单、管理用户 (✅ v1.1) |

---

## 🔧 密码加密

### 加密算法

使用 **bcrypt** 算法进行密码加密

### 使用方法

**加密**:
```python
import bcrypt

password = "SecurePass123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
```

**验证**:
```python
is_valid = bcrypt.checkpw(
    password.encode('utf-8'),
    hashed
)
```

### 特点

- 单向加密（不可逆）
- 自动加盐（Salt）
- 计算成本可调
- 业界标准安全算法

---

## 📝 版本更新日志

### v1.1 (2025-10-22) - Current

#### 🎯 核心功能更新

**订单审核流程**:
- ✅ 新增 `pending_review` 订单状态
- ✅ 订单发布后需要管理员审核
- ✅ 新增 `order.approved` 事件
- ✅ 新增 `order.rejected` 事件（包含拒绝原因）

**订单字段增强**:
- ✅ 新增 `service_type` 字段（6种服务类型）
- ✅ 新增 `service_start_time` 字段
- ✅ 新增 `service_end_time` 字段

#### 📡 API 更新

**Admin Order API（6个新接口）**:
- ✅ `GET /admin/orders` - 获取所有订单（支持状态过滤）
- ✅ `GET /admin/orders/pending-review` - 获取待审核订单
- ✅ `GET /admin/orders/{order_id}` - 获取订单详情
- ✅ `POST /admin/orders/{order_id}/approve` - 审批订单
- ✅ `PUT /admin/orders/{order_id}` - 更新订单信息
- ✅ `DELETE /admin/orders/{order_id}` - 删除订单

**Order Detail API（2个新接口）**:
- ✅ `GET /customer/orders/my/{order_id}` - 客户查看订单详情
- ✅ `GET /provider/orders/my/{order_id}` - 服务商查看订单详情

**API 响应优化**:
- ✅ 所有订单列表接口返回完整 OrderDetail（17字段，之前7字段）
- ✅ 受影响接口：
  - `/customer/orders/my`
  - `/customer/orders/history`
  - `/provider/orders/available`
  - `/provider/orders/history`
  - `/admin/orders`
  - `/admin/orders/pending-review`

#### 💰 Payment Service 简化

- ✅ 移除充值功能（`POST /customer/payments/recharge`）
- ✅ 改为模拟支付，无需余额验证
- ✅ 简化用户支付流程

#### 🔔 Notification Service 增强

- ✅ 新增订单审核通过通知
- ✅ 新增订单审核拒绝通知（包含拒绝原因）

#### 🔌 Gateway Service 更新

- ✅ 新增 Admin 订单管理路由
- ✅ 新增 Customer/Provider 订单详情路由

#### 🗄️ 数据模型更新

- ✅ Orders 表新增 3 个字段
- ✅ 订单状态枚举新增 `pending_review`
- ✅ 事件系统新增 2 个事件类型

---

### v1.0 (2025-10-17)

- 初始版本发布
- 完整的微服务架构实现
- 基础 CRUD 功能
- 事件驱动架构
- JWT 认证和授权

---

## 🎯 Monolith 迁移指南

### 架构转换建议

**微服务 → Monolith 转换要点**:

1. **合并数据库**:
   - **MySQL**: 合并 Auth Service、Order Service、Payment Service 的表到一个数据库
     - `users` 表（Auth Service）
     - `roles` 表（Auth Service）
     - `orders` 表（Order Service）
     - `payments` 表（Payment Service）
   - **MongoDB**: 合并所有集合到一个数据库
     - `customer_profiles` 集合（User Service）
     - `provider_profiles` 集合（User Service）
     - `reviews` 集合（Review Service）
     - `notifications` 集合（Notification Service）
   - 保持所有表结构和字段定义不变

2. **移除 RabbitMQ**:
   - 将事件发布改为直接函数调用
   - 或使用应用内事件总线（如 Django Signals）

3. **合并服务**:
   - 将所有服务合并为一个应用
   - 保持 API 路由结构
   - 移除 Gateway Service 的路由转发

4. **保留的功能**:
   - ✅ JWT 认证
   - ✅ 所有 API 端点
   - ✅ 业务逻辑
   - ✅ 数据库结构（MySQL + MongoDB）
   - ✅ 订单审核流程
   - ✅ User Service 的 MongoDB 数据模型

5. **推荐技术栈**（Monolith）:
   - Django / Django REST Framework
   - MySQL 8.0（用户、订单、支付）
   - MongoDB 6.0（用户资料、评价、通知）
   - Redis（缓存）
   - Motor（异步 MongoDB 驱动）

---

## 📞 技术支持

**文档版本**: v1.1  
**最后更新**: 2025-10-22  
**维护团队**: Backend Development Team

如有技术问题，请查阅各服务的 README.md 或联系开发团队。

---

## 📚 附录

### A. 环境变量配置示例

```env
# Database
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/freelancer
MONGODB_URL=mongodb://localhost:27017/freelancer

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# JWT
SECRET_KEY=your-secret-key-here
JWT_EXPIRATION=1800

# Services URLs (仅微服务架构需要)
AUTH_SERVICE_URL=http://localhost:8000
USER_SERVICE_URL=http://localhost:8002
ORDER_SERVICE_URL=http://localhost:8003
PAYMENT_SERVICE_URL=http://localhost:8004
REVIEW_SERVICE_URL=http://localhost:8005
NOTIFICATION_SERVICE_URL=http://localhost:8006
```

### B. API 响应格式

**成功响应**:
```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

**错误响应**:
```json
{
  "success": false,
  "data": null,
  "message": "错误描述",
  "error": "详细错误信息"
}
```

### C. HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器错误 |

---

**文档结束**
