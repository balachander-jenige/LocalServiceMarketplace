# Architecture Presentation Guide

## 图1: Logical Architecture Diagram（逻辑架构图）

### 架构概述
本项目采用**微服务架构**，通过API Gateway统一入口，实现服务解耦和独立部署。

### 五层架构说明

#### 1. Frontend Layer（前端层）
- **技术栈**: Vue.js 3 + Vite
- **用户角色**: Customer（客户）、Provider（服务提供商）、Admin（管理员）
- **位置**: `frontend/src/views/` 目录
- **说明**: 提供三种角色的Web界面，通过REST API与后端通信

#### 2. API Gateway Layer（网关层）
- **技术栈**: FastAPI (Python)
- **端口**: 8080
- **核心功能**:
  - 路由转发 (`gateway-service/src/gateway_service/api/routes.py`)
  - JWT认证 (`core/jwt_handler.py`)
  - 限流保护 (`core/rate_limiter.py`)
- **说明**: 统一入口，所有前端请求先经过网关验证后再转发到对应服务

#### 3. Microservices Layer（微服务层）
6个独立服务，各司其职：

| 服务 | 端口 | 数据库 | 核心职责 | 代码位置 |
|-----|------|--------|---------|---------|
| **Auth Service** | 8000 | MySQL | 用户注册/登录、JWT颁发 | `services/auth-service/src/auth_service/services/auth_service.py` |
| **User Service** | 8002 | MongoDB | 用户资料管理、Provider认证 | `services/user-service/src/user_service/services/user_service.py` |
| **Order Service** | 8003 | MySQL | 订单创建、状态流转、订单分配 | `services/order-service/src/order_service/services/` |
| **Payment Service** | 8004 | MySQL | 支付处理、退款管理 | `services/payment-service/src/payment_service/services/payment_service.py` |
| **Review Service** | 8005 | MongoDB | 评价提交、评分统计 | `services/review-service/src/review_service/services/review_service.py` |
| **Notification Service** | 8006 | MongoDB | 消息推送、事件驱动通知 | `services/notification-service/src/notification_service/events/handlers/` |

#### 4. Infrastructure Layer（基础设施层）
- **缓存**: Redis（会话管理、限流计数）
- **消息队列**: RabbitMQ（异步事件通信）
  - 5个Exchange: `order_events`, `payment_events`, `review_events`, `auth_events`, `user_events`
  - 代码示例: `shared/common/messaging/message_publisher.py`

#### 5. Database Layer（数据库层）
**Polyglot Persistence（多语言持久化）**策略：
- **MySQL**: 事务性数据（Auth、Order、Payment）
- **MongoDB**: 灵活文档（User、Review、Notification）

---

## 图2: DDD Diagram（领域驱动设计图）

### 核心理念
每个服务都是一个**独立的领域**，拥有自己的模型、业务逻辑和数据存储。

### 服务领域详解

#### 1. API Gateway Service（网关服务）
**职责**: 
- ✅ Route requests（路由请求）
- ✅ Authenticate users（用户认证）
- ✅ Rate limiting（流量控制）

**关键代码**:
```python
# gateway-service/src/gateway_service/api/routes.py
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request, ...):
    # 1. JWT验证
    # 2. 路由转发
    # 3. 限流检查
```

#### 2. Auth Service（认证服务领域）
**职责**:
- ✅ User registration（用户注册）
- ✅ Login/Logout（登录登出）
- ✅ JWT token management（令牌管理）

**核心模型**:
```python
# services/auth-service/src/auth_service/models/user.py
class User(Base):
    id: int                    # 用户ID
    username: str              # 用户名
    email: str                 # 邮箱
    password_hash: str         # 密码哈希
    role_id: int               # 角色ID（1=Customer, 2=Provider, 3=Admin）
```

**数据库**: MySQL - `auth_db` (users, roles)

#### 3. User Service（用户服务领域）
**职责**:
- ✅ Manage user profiles（管理用户资料）

**核心功能**:
- Customer: 更新个人信息、地址、联系方式
- Provider: 上传资质证书、设置服务区域、技能标签
- Admin: 审核Provider资质

**数据库**: MongoDB - `user_db` (users集合，支持灵活schema)

#### 4. Order Service（订单服务领域）
**职责**:
- ✅ Create orders（创建订单）
- ✅ Track order status（追踪订单状态）
- ✅ Manage order lifecycle（管理订单生命周期）
- ✅ Order detail & history（订单详情与历史）

**订单状态流转**:
```
pending_review → pending → accepted → in_progress → completed → reviewed
                    ↓
                cancelled
```

**关键代码**:
```python
# services/order-service/src/order_service/models/order.py
class Order(Base):
    service_type: ServiceType   # 服务类型（清洁维修、IT技术等）
    status: OrderStatus         # 订单状态
    location: Location          # 服务区域（NORTH/SOUTH/EAST/WEST/MID）
    payment_status: PaymentStatus  # 支付状态
```

**数据库**: MySQL - `order_db` (orders表)

#### 5. Payment Service（支付服务领域）
**职责**:
- ✅ Process payments（处理支付）
- ✅ Manage transactions（管理交易）

**事件驱动**:
```python
# 支付完成后发布事件
await publish_event(
    exchange="payment_events",
    routing_key="payment.completed",
    message={"order_id": order_id, "amount": amount}
)
```

**数据库**: MySQL - `payment_db` (payments, refunds)

#### 6. Review Service（评价服务领域）
**职责**:
- ✅ Submit reviews（提交评价）
- ✅ Rating system（评分系统）
- ✅ Review moderation（评价审核）

**核心流程**:
1. Order完成 → 允许Customer评价
2. 评价包含: 评分(1-5)、评论内容、服务态度、专业程度
3. 发布 `review.created` 事件 → 更新Provider评分

**数据库**: MongoDB - `review_db` (reviews集合)

#### 7. Notification Service（通知服务领域）
**职责**:
- ✅ Send order notifications（发送订单通知）
- ✅ Send admin notifications（发送管理通知）
- ✅ Event-driven messaging（事件驱动消息）

**事件消费者**:
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py
async def handle_order_created(message: dict):
    # 订单创建 → 通知Customer和匹配的Providers
    
async def handle_order_accepted(message: dict):
    # 订单接受 → 通知Customer和Provider
```

**数据库**: MongoDB - `notification_db` (notifications集合)

---

## 图3: Event-Driven Architecture（事件驱动架构图）

### 架构概述
采用**Producer-Consumer模式**，通过RabbitMQ实现服务间的异步解耦通信。

### 事件流转三层结构

#### Layer 1: Event Producers（事件生产者）
5个服务作为事件发布者，各自发布领域事件：

**Auth Service**:
- `user.registered` - 新用户注册完成

**Payment Service**:
- `payment.initiated` - 支付发起
- `payment.completed` - 支付完成
- `payment.failed` - 支付失败

**Review Service**:
- `review.created` - 评价创建
- `rating.updated` - 评分更新

**Order Service** (最核心的事件源):
- `order.created` - 订单创建
- `order.accepted` - Provider接受订单
- `order.cancelled` - 订单取消
- `order.status_changed` - 订单状态变更
- `order.approved` - 管理员审核通过
- `order.rejected` - 管理员拒绝订单

**User Service**:
- `profile.created` - 用户资料创建
- `profile.updated` - 用户资料更新

#### Layer 2: Event Bus (RabbitMQ)

**Exchange配置** (Topic类型):
```python
# 5个Topic Exchange，支持路由键模式匹配
auth_events     # 路由键: user.*
payment_events  # 路由键: payment.*
review_events   # 路由键: review.*, rating.*
order_events    # 路由键: order.*
user_events     # 路由键: profile.*
```

**Queue绑定** (3个核心队列):
```python
# shared/common/messaging/message_publisher.py
payment_queue:
  - Bindings: payment.*
  - 用途: Payment Service处理支付事务
  
review_queue:
  - Bindings: review.*
  - 用途: Review Service处理评价逻辑
  
order_queue:
  - Bindings: order.*
  - 用途: Notification Service监听订单事件
```

**实际代码示例**:
```python
# shared/common/messaging/message_publisher.py
async def publish_event(exchange: str, routing_key: str, message: dict):
    """统一的事件发布接口"""
    channel = await get_rabbitmq_channel()
    
    await channel.exchange_declare(
        exchange=exchange,
        exchange_type='topic',  # Topic类型支持通配符
        durable=True
    )
    
    await channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(message).encode(),
        properties=aiormq.spec.Basic.Properties(
            delivery_mode=2  # 持久化消息
        )
    )
```

#### Layer 3: Event Consumer（事件消费者）

**Notification Service** - 唯一的多事件消费者:
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py

async def handle_order_created(message: dict):
    """订单创建 → 通知匹配的Providers"""
    # 1. 查询符合条件的Provider（区域、技能匹配）
    # 2. 创建通知记录
    # 3. 推送到Provider的inbox

async def handle_order_accepted(message: dict):
    """订单接受 → 通知Customer和Provider"""
    # 1. 通知Customer: "您的订单已被接受"
    # 2. 通知Provider: "请按时完成服务"

async def handle_payment_completed(message: dict):
    """支付完成 → 通知双方"""
    # 1. 通知Customer: "支付成功"
    # 2. 通知Provider: "款项已托管"

async def handle_review_created(message: dict):
    """评价创建 → 通知Provider"""
    # 通知Provider: "您收到了新的评价"
```

**订阅配置**:
```python
# services/notification-service/src/notification_service/events/consumer.py
SUBSCRIPTIONS = [
    "payment.initiated",
    "payment.completed",
    "payment.failed",
    "review.created",
    "rating.updated",
    "order.created",
    "order.accepted",
    "order.cancelled",
    "order.status_changed",
    "order.approved",
    "order.rejected"
]
```

### 事件驱动优势

✅ **解耦**: Order Service不需要知道Notification Service的存在  
✅ **异步**: 订单创建立即返回，通知推送在后台完成  
✅ **可扩展**: 新增Consumer无需修改Producer代码  
✅ **容错**: RabbitMQ持久化保证消息不丢失  
✅ **灵活路由**: Topic Exchange支持复杂的订阅模式

### 典型事件流示例

**场景: Customer发布订单**
```
1. Order Service → publish("order_events", "order.created", {...})
2. RabbitMQ → route to order_queue (binding: order.*)
3. Notification Service → consume from order_queue
4. Notification Service → 查询匹配Providers → 推送通知
```

**场景: 支付完成联动**
```
1. Payment Service → publish("payment_events", "payment.completed", {order_id: 123})
2. RabbitMQ → route to payment_queue
3. Order Service → 更新order.payment_status = 'paid'
4. Order Service → publish("order_events", "order.status_changed", {...})
5. Notification Service → 通知Customer支付成功
```

---

## 图4: Polyglot Persistence（多语言持久化架构图）

### 架构概述
根据不同服务的数据特性，选择**最适合的数据库技术**，实现技术栈多样化。

### 两类数据库部署

#### AWS RDS MySQL 8.0（关系型数据库）
用于**事务性强、一致性要求高**的业务场景。

**Auth Database (MySQL)**:
- **部署**: AWS RDS MySQL 8.0 实例
- **ORM**: SQLAlchemy (异步)
- **表结构**:
  ```sql
  -- users表
  CREATE TABLE users (
      id BIGINT PRIMARY KEY AUTO_INCREMENT,
      username VARCHAR(100) UNIQUE NOT NULL,
      email VARCHAR(255) UNIQUE NOT NULL,
      password_hash VARCHAR(255) NOT NULL,
      role_id INT NOT NULL,
      is_active BOOLEAN DEFAULT TRUE,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (role_id) REFERENCES roles(id)
  );
  
  -- roles表
  CREATE TABLE roles (
      id INT PRIMARY KEY AUTO_INCREMENT,
      name VARCHAR(50) UNIQUE NOT NULL  -- 'customer', 'provider', 'admin'
  );
  ```
- **代码位置**: `services/auth-service/src/auth_service/models/user.py`
- **为什么选MySQL**: 用户认证需要ACID特性，防止重复注册和角色混乱

**Order Database (MySQL)**:
- **部署**: AWS RDS MySQL 8.0 实例
- **ORM**: SQLAlchemy (异步)
- **表结构**:
  ```sql
  CREATE TABLE orders (
      id BIGINT PRIMARY KEY AUTO_INCREMENT,
      customer_id BIGINT NOT NULL,
      provider_id BIGINT NULL,
      service_type ENUM('cleaning_repair', 'it_technology', ...) NOT NULL,
      status ENUM('pending_review', 'pending', 'accepted', ...) DEFAULT 'pending_review',
      location ENUM('NORTH', 'SOUTH', 'EAST', 'WEST', 'MID') NOT NULL,
      payment_status ENUM('unpaid', 'paid') DEFAULT 'unpaid',
      amount DECIMAL(10,2) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  );
  ```
- **代码位置**: `services/order-service/src/order_service/models/order.py`
- **为什么选MySQL**: 订单状态流转需要事务保证，避免状态不一致

**Payment Database (MySQL)**:
- **部署**: AWS RDS MySQL 8.0 实例
- **ORM**: SQLAlchemy (异步)
- **表结构**:
  ```sql
  -- payments表
  CREATE TABLE payments (
      id BIGINT PRIMARY KEY AUTO_INCREMENT,
      order_id BIGINT NOT NULL,
      transaction_id VARCHAR(255) UNIQUE NOT NULL,
      amount DECIMAL(10,2) NOT NULL,
      status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
      payment_method VARCHAR(50),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  
  -- transactions表（支付流水）
  CREATE TABLE transactions (
      id BIGINT PRIMARY KEY AUTO_INCREMENT,
      payment_id BIGINT NOT NULL,
      action VARCHAR(50) NOT NULL,  -- 'charge', 'refund', 'hold'
      amount DECIMAL(10,2) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (payment_id) REFERENCES payments(id)
  );
  ```
- **代码位置**: `services/payment-service/src/payment_service/models/payment.py`
- **为什么选MySQL**: 支付交易必须保证ACID，防止资金损失

#### MongoDB Atlas 7.0（文档型数据库）
用于**灵活schema、读多写少**的业务场景。

**User Database (MongoDB)**:
- **部署**: MongoDB Atlas 7.0 集群
- **Driver**: Motor (异步MongoDB驱动)
- **Collections**:
  ```javascript
  // customer_profiles集合
  {
      _id: ObjectId,
      user_id: 123,  // 关联auth_db.users.id
      full_name: "张三",
      phone: "13800138000",
      address: {
          province: "北京市",
          city: "海淀区",
          detail: "中关村大街1号"
      },
      preferences: {
          location: "NORTH",
          service_types: ["it_technology", "cleaning_repair"]
      },
      created_at: ISODate("2025-10-25T10:00:00Z")
  }
  
  // provider_profiles集合（schema更灵活）
  {
      _id: ObjectId,
      user_id: 456,
      full_name: "李四",
      skills: ["网络维修", "电脑组装", "系统安装"],
      certifications: [
          {name: "计算机维修技师", file_url: "https://..."}
      ],
      service_areas: ["NORTH", "MID"],
      rating: 4.8,
      completed_orders: 156,
      verified: true
  }
  ```
- **代码位置**: `services/user-service/src/user_service/services/user_service.py`
- **为什么选MongoDB**: 用户资料字段差异大（Customer vs Provider），MongoDB灵活schema更合适

**Review Database (MongoDB)**:
- **部署**: MongoDB Atlas 7.0 集群
- **Driver**: Motor (异步)
- **Collections**:
  ```javascript
  // reviews集合
  {
      _id: ObjectId,
      order_id: 789,
      customer_id: 123,
      provider_id: 456,
      rating: 5,  // 1-5星
      comment: "服务态度好，技术专业",
      dimensions: {  // 多维度评分
          professionalism: 5,
          attitude: 5,
          punctuality: 4
      },
      images: ["https://...", "https://..."],
      created_at: ISODate("2025-10-25T15:00:00Z")
  }
  
  // ratings集合（聚合统计）
  {
      _id: ObjectId,
      provider_id: 456,
      average_rating: 4.8,
      total_reviews: 156,
      rating_distribution: {
          "5": 120,
          "4": 30,
          "3": 5,
          "2": 1,
          "1": 0
      }
  }
  ```
- **代码位置**: `services/review-service/src/review_service/services/review_service.py`
- **为什么选MongoDB**: 评价内容多样（文字、图片、多维度评分），MongoDB更灵活

**Notification Database (MongoDB)**:
- **部署**: MongoDB Atlas 7.0 集群
- **Driver**: Motor (异步)
- **Collections**:
  ```javascript
  // customer_inbox集合
  {
      _id: ObjectId,
      user_id: 123,
      type: "order_update",
      title: "订单已被接受",
      content: "Provider李四已接受您的订单，请及时支付",
      order_id: 789,
      is_read: false,
      created_at: ISODate("2025-10-25T12:00:00Z")
  }
  
  // provider_inbox集合
  {
      _id: ObjectId,
      user_id: 456,
      type: "new_order",
      title: "新订单通知",
      content: "您有一个新的订单匹配，请查看",
      order_id: 789,
      is_read: false,
      created_at: ISODate("2025-10-25T11:00:00Z")
  }
  ```
- **代码位置**: `services/notification-service/src/notification_service/services/notification_service.py`
- **为什么选MongoDB**: 通知消息是追加型数据，MongoDB写入性能更好

### 数据库连接配置

**MySQL连接（SQLAlchemy异步）**:
```python
# services/auth-service/src/auth_service/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine(
    "mysql+aiomysql://user:password@auth-db-instance.rds.amazonaws.com:3306/auth_db",
    echo=True,
    pool_size=10,
    max_overflow=20
)
```

**MongoDB连接（Motor异步）**:
```python
# services/user-service/src/user_service/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    "mongodb+srv://user:password@user-cluster.mongodb.net/user_db?retryWrites=true&w=majority"
)
db = client.user_db
```

### Polyglot Persistence优势

✅ **技术选型自由**: 按数据特性选择最优方案  
✅ **性能优化**: MySQL保证事务，MongoDB提升读写速度  
✅ **成本控制**: MongoDB Atlas按需扩展，节省成本  
✅ **风险隔离**: 数据库故障不会影响所有服务  
✅ **团队专业**: 不同团队可使用熟悉的技术栈

### 数据一致性策略

**跨数据库关联**:
```python
# 示例：Order Service需要Customer信息
# 1. 从order_db获取order.customer_id
# 2. 通过API调用User Service获取customer详情
# 3. 不做数据库级别的JOIN
```

**最终一致性**:
```python
# 示例：支付完成后更新订单状态
# 1. Payment Service: payment.status = 'completed'
# 2. 发布event: payment.completed
# 3. Order Service: 监听事件 → order.payment_status = 'paid'
# 4. 存在短暂延迟（毫秒级），但最终一致
```

---

## 服务间通信模式

### 同步通信（Synchronous）
- **方式**: REST API
- **场景**: Gateway → Services、Service → Service（需要立即响应）
- **示例**: Payment Service查询Order详情

### 异步通信（Asynchronous）
- **方式**: RabbitMQ事件
- **场景**: 状态变更通知、跨服务数据同步
- **示例**: 
  - `order.accepted` → Payment Service创建待支付记录
  - `payment.completed` → Order Service更新支付状态
  - `order.completed` → Review Service允许评价

---

## 关键设计模式

### 1. API Gateway Pattern（网关模式）
- 统一入口，简化前端调用
- 集中认证授权
- 负载均衡和限流

### 2. Event-Driven Architecture（事件驱动架构）
- 服务解耦，降低依赖
- 异步处理，提升性能
- 事件溯源，便于审计

### 3. Polyglot Persistence（多语言持久化）
- MySQL: ACID事务保证（订单、支付）
- MongoDB: 灵活schema（用户资料、评价）
- Redis: 高速缓存（限流、会话）

### 4. Database per Service（每服务独立数据库）
- 数据隔离，独立扩展
- 技术栈自由选择
- 避免单点故障

---

## Presentation Tips（演示技巧）

### 讲解顺序建议
1. **图1 - Logical Architecture**: 从上到下（Frontend → Gateway → Services → Infrastructure → Database）
2. **图2 - DDD Diagram**: 按业务流程（Auth → Order → Payment → Review → Notification）
3. **图3 - Event-Driven Architecture**: 从左到右（Producers → Exchanges → Queues → Consumer）
4. **图4 - Polyglot Persistence**: 按数据库类型（MySQL事务型 vs MongoDB文档型）
5. **综合案例**: 以"Customer发布订单"串联所有架构图

### 四张图的关系
```
图1 (Logical) - 整体架构全景，从宏观角度看系统分层
    ↓
图2 (DDD) - 微服务职责细化，每个服务的领域边界
    ↓
图3 (Event-Driven) - 服务间异步通信机制，解耦策略
    ↓
图4 (Polyglot) - 数据存储选型，技术栈多样化
```

### 关键亮点
✨ **微服务架构**: 6个独立服务，可独立部署扩展  
✨ **事件驱动**: 15+事件类型，实现服务解耦  
✨ **多数据库策略**: 3个MySQL + 3个MongoDB，按需选型  
✨ **API Gateway**: 统一认证、限流、路由，简化前端调用  
✨ **DDD设计**: 每个服务都是独立领域，清晰的职责边界  
✨ **RabbitMQ**: 5个Exchange + 3个Queue，灵活路由  
✨ **AWS云部署**: RDS实例 + MongoDB Atlas，高可用架构

### 讲解重点（每张图）

**图1 重点**: 
- 强调API Gateway的中心地位
- 解释为什么用Redis做缓存、RabbitMQ做消息队列
- 说明6个服务的端口号和技术栈

**图2 重点**:
- 每个服务的核心职责（3-4条）
- Order Service是业务核心（订单状态流转）
- Notification Service是唯一的事件消费者

**图3 重点**:
- Producer-Consumer解耦模式
- Topic Exchange的路由机制（通配符匹配）
- 举例：`order.created`如何从Order Service流转到Notification Service

**图4 重点**:
- MySQL vs MongoDB的选型依据
- Auth/Order/Payment为什么必须用MySQL（ACID）
- User/Review/Notification为什么适合MongoDB（灵活schema）
- 展示实际的表结构和Collection文档

### 可能的问题准备
**Q: 为什么不用单体架构？**  
A: 微服务支持独立部署、技术栈灵活、团队并行开发，适合复杂业务场景。

**Q: 服务间如何保证数据一致性？**  
A: 使用事件驱动 + 最终一致性模型，关键事务用MySQL的ACID特性保证。

**Q: 如果RabbitMQ宕机怎么办？**  
A: 核心流程（下单、支付）是同步的，通知类功能可降级，RabbitMQ支持集群和持久化。

**Q: 为什么有些服务用MySQL，有些用MongoDB？**  
A: 根据数据特性选型 - 事务性强的用MySQL（订单、支付），schema灵活的用MongoDB（用户资料、评价）。

**Q: Event-Driven和REST API有什么区别？**  
A: REST是同步调用（等待响应），Event是异步通知（发完就走），各有适用场景。

**Q: 一个订单从创建到完成要经过多少个服务？**  
A: 至少5个 - Order（创建）→ Notification（通知Provider）→ Payment（支付）→ Order（状态更新）→ Review（评价）。

---

## 代码演示路径

如需现场演示代码，建议路径：

### 图1 & 图2 相关代码
1. **Gateway路由**: `gateway-service/src/gateway_service/api/routes.py` (第58-89行)
2. **订单创建**: `services/order-service/src/order_service/services/customer_order_service.py` (第26-80行)
3. **数据模型**: `services/order-service/src/order_service/models/order.py` (查看完整字段定义)

### 图3 (Event-Driven) 相关代码
4. **事件发布器**: `shared/common/messaging/message_publisher.py` (第15-32行)
   ```python
   # 展示如何发布事件到RabbitMQ
   await publish_event(
       exchange="order_events",
       routing_key="order.created",
       message={...}
   )
   ```

5. **事件消费者**: `services/notification-service/src/notification_service/events/consumer.py`
   ```python
   # 展示如何订阅多个事件
   SUBSCRIPTIONS = [
       "order.created",
       "payment.completed",
       ...
   ]
   ```

6. **事件处理器**: `services/notification-service/src/notification_service/events/handlers/order_event_handler.py` (第20-59行)
   ```python
   # 展示order.created事件的处理逻辑
   async def handle_order_created(message: dict):
       # 查询匹配的Providers
       # 创建通知记录
       # 推送到inbox
   ```

### 图4 (Polyglot Persistence) 相关代码

**MySQL相关**:
7. **Auth数据库配置**: `services/auth-service/src/auth_service/core/database.py`
   ```python
   # 展示SQLAlchemy异步引擎配置
   engine = create_async_engine(
       "mysql+aiomysql://...",
       pool_size=10
   )
   ```

8. **User模型（MySQL）**: `services/auth-service/src/auth_service/models/user.py`
   ```python
   # 展示SQLAlchemy ORM模型定义
   class User(Base):
       __tablename__ = "users"
       id = Column(BigInteger, primary_key=True)
       ...
   ```

9. **Order模型（MySQL）**: `services/order-service/src/order_service/models/order.py`
   ```python
   # 展示ENUM字段定义
   class ServiceType(str, Enum):
       CLEANING_REPAIR = "cleaning_repair"
       IT_TECHNOLOGY = "it_technology"
       ...
   ```

**MongoDB相关**:
10. **User数据库配置**: `services/user-service/src/user_service/core/database.py`
    ```python
    # 展示Motor异步MongoDB客户端
    client = AsyncIOMotorClient("mongodb+srv://...")
    db = client.user_db
    ```

11. **User Service（MongoDB操作）**: `services/user-service/src/user_service/services/user_service.py`
    ```python
    # 展示MongoDB的灵活查询
    async def get_customer_profile(user_id: int):
        profile = await db.customer_profiles.find_one({"user_id": user_id})
        return profile
    ```

12. **Review Service（MongoDB聚合）**: `services/review-service/src/review_service/services/review_service.py`
    ```python
    # 展示MongoDB的聚合管道
    async def calculate_provider_rating(provider_id: int):
        pipeline = [
            {"$match": {"provider_id": provider_id}},
            {"$group": {"_id": "$provider_id", "avg": {"$avg": "$rating"}}}
        ]
        result = await db.reviews.aggregate(pipeline).to_list(1)
    ```

### 演示建议顺序
1. 先展示MySQL的严格schema（User/Order模型）
2. 再展示MongoDB的灵活document（Customer/Provider profiles差异）
3. 对比两种数据库的连接配置代码
4. 演示事件发布和消费的完整流程
5. 最后回到架构图，总结技术选型的合理性

---

## 综合案例：Customer发布订单全流程

通过一个完整的业务流程，串联所有4张架构图。

### 业务场景
Customer张三发布一个"电脑维修"订单，期望Provider李四接单并完成服务。

### 流程详解（结合4张图）

#### 阶段1: 用户认证（图1 + 图2）

**前端操作**:
```javascript
// Frontend (Vue.js)
POST http://localhost:8080/api/auth/login
{
  "username": "zhangsan",
  "password": "password123"
}
```

**架构流转**:
```
Frontend (图1-Layer1) 
  → API Gateway (图1-Layer2, 图2-Gateway Service)
    → Auth Service (图1-Layer3, 图2-Auth Service)
      → MySQL auth_db (图1-Layer5, 图4-Auth Database)
```

**数据库操作（图4 - MySQL）**:
```sql
-- Auth Service查询用户
SELECT id, username, password_hash, role_id 
FROM users 
WHERE username = 'zhangsan';

-- 验证密码后，返回JWT Token
```

**返回结果**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": 123,
  "role": "customer"
}
```

---

#### 阶段2: 创建订单（图1 + 图2 + 图4）

**前端操作**:
```javascript
// Frontend
POST http://localhost:8080/api/orders/
Headers: { "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..." }
{
  "service_type": "it_technology",
  "location": "NORTH",
  "description": "电脑无法开机，需要检修",
  "amount": 200.00
}
```

**架构流转**:
```
Frontend 
  → API Gateway (JWT验证 + 限流检查)
    → Order Service (图2-Order Service)
      → MySQL order_db (图4-Order Database)
```

**Order Service代码**:
```python
# services/order-service/src/order_service/services/customer_order_service.py
async def publish_order(customer_id: int, order_data: dict):
    # 1. 创建订单（状态: pending_review）
    order = Order(
        customer_id=customer_id,
        service_type=order_data['service_type'],
        location=order_data['location'],
        status=OrderStatus.PENDING_REVIEW,
        payment_status=PaymentStatus.UNPAID,
        amount=order_data['amount']
    )
    db.add(order)
    await db.commit()
    
    # 2. 发布事件（图3 - Event-Driven）
    await publish_event(
        exchange="order_events",
        routing_key="order.created",
        message={
            "order_id": order.id,
            "customer_id": customer_id,
            "service_type": order_data['service_type'],
            "location": order_data['location']
        }
    )
    
    return order
```

**数据库操作（图4 - MySQL）**:
```sql
-- Order Database
INSERT INTO orders 
(customer_id, service_type, location, status, payment_status, amount, created_at)
VALUES 
(123, 'it_technology', 'NORTH', 'pending_review', 'unpaid', 200.00, NOW());
```

---

#### 阶段3: 事件驱动通知（图3 - Event-Driven）

**事件发布（Producer）**:
```
Order Service 
  → publish to RabbitMQ
    → Exchange: order_events (Topic)
      → Routing Key: order.created
```

**RabbitMQ路由（图3 - Event Bus）**:
```
order_events Exchange 
  → route to order_queue (binding: order.*)
    → Notification Service subscribes to order_queue
```

**事件消费（Consumer）**:
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py
async def handle_order_created(message: dict):
    order_id = message['order_id']
    location = message['location']
    service_type = message['service_type']
    
    # 1. 查询匹配的Providers（图4 - MongoDB）
    providers = await db.provider_profiles.find({
        "service_areas": location,
        "skills": {"$in": ["电脑维修", "硬件维修"]},
        "verified": True
    }).to_list(10)
    
    # 2. 创建通知记录
    for provider in providers:
        notification = {
            "user_id": provider['user_id'],
            "type": "new_order",
            "title": "新订单通知",
            "content": f"您有一个新的{service_type}订单",
            "order_id": order_id,
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        await db.provider_inbox.insert_one(notification)
    
    # 3. 通知Customer
    await db.customer_inbox.insert_one({
        "user_id": message['customer_id'],
        "type": "order_created",
        "title": "订单创建成功",
        "content": "您的订单已发布，等待Provider接单",
        "order_id": order_id,
        "is_read": False,
        "created_at": datetime.utcnow()
    })
```

**数据库操作（图4 - MongoDB）**:
```javascript
// Notification Database - MongoDB
db.provider_inbox.insertMany([
    {
        user_id: 456,  // Provider李四
        type: "new_order",
        title: "新订单通知",
        order_id: 789,
        is_read: false,
        created_at: ISODate("2025-10-25T10:00:00Z")
    },
    // ... 其他匹配的Providers
]);

db.customer_inbox.insertOne({
    user_id: 123,  // Customer张三
    type: "order_created",
    title: "订单创建成功",
    order_id: 789,
    is_read: false
});
```

---

#### 阶段4: Provider接单（图1 + 图2 + 图3 + 图4）

**Provider操作**:
```javascript
// Provider李四查看通知后，决定接单
PUT http://localhost:8080/api/orders/789/accept
Headers: { "Authorization": "Bearer <provider_token>" }
```

**Order Service代码**:
```python
# services/order-service/src/order_service/services/provider_order_service.py
async def accept_order(order_id: int, provider_id: int):
    # 1. 更新订单（图4 - MySQL）
    order = await db.get(Order, order_id)
    order.provider_id = provider_id
    order.status = OrderStatus.ACCEPTED
    await db.commit()
    
    # 2. 发布事件（图3）
    await publish_event(
        exchange="order_events",
        routing_key="order.accepted",
        message={
            "order_id": order_id,
            "provider_id": provider_id,
            "customer_id": order.customer_id
        }
    )
    
    return order
```

**数据库更新（图4 - MySQL）**:
```sql
UPDATE orders 
SET provider_id = 456, status = 'accepted', updated_at = NOW()
WHERE id = 789;
```

**事件流转（图3）**:
```
Order Service → order_events Exchange → order_queue → Notification Service
```

**Notification处理**:
```python
async def handle_order_accepted(message: dict):
    # 通知Customer
    await db.customer_inbox.insert_one({
        "user_id": message['customer_id'],
        "type": "order_accepted",
        "title": "订单已被接受",
        "content": "Provider已接受您的订单，请及时支付",
        "order_id": message['order_id']
    })
    
    # 通知Provider
    await db.provider_inbox.insert_one({
        "user_id": message['provider_id'],
        "type": "order_accepted",
        "title": "接单成功",
        "content": "您已成功接单，请等待Customer支付",
        "order_id": message['order_id']
    })
```

---

#### 阶段5: 支付流程（图2 + 图3 + 图4）

**Customer支付**:
```javascript
POST http://localhost:8080/api/payments/
{
  "order_id": 789,
  "amount": 200.00,
  "payment_method": "alipay"
}
```

**Payment Service代码**:
```python
# services/payment-service/src/payment_service/services/payment_service.py
async def process_payment(order_id: int, amount: Decimal):
    # 1. 创建支付记录（图4 - MySQL）
    payment = Payment(
        order_id=order_id,
        amount=amount,
        status=PaymentStatus.PENDING,
        transaction_id=generate_transaction_id()
    )
    db.add(payment)
    await db.commit()
    
    # 2. 调用第三方支付API（支付宝）
    result = await alipay_api.charge(
        amount=amount,
        transaction_id=payment.transaction_id
    )
    
    # 3. 更新支付状态
    if result.success:
        payment.status = PaymentStatus.COMPLETED
        await db.commit()
        
        # 4. 发布事件（图3）
        await publish_event(
            exchange="payment_events",
            routing_key="payment.completed",
            message={
                "payment_id": payment.id,
                "order_id": order_id,
                "amount": float(amount)
            }
        )
```

**数据库操作（图4 - MySQL）**:
```sql
-- Payment Database
INSERT INTO payments 
(order_id, transaction_id, amount, status, created_at)
VALUES 
(789, 'TXN-2025102512345', 200.00, 'completed', NOW());

INSERT INTO transactions
(payment_id, action, amount, created_at)
VALUES
(1, 'charge', 200.00, NOW());
```

**事件联动（图3）**:
```
Payment Service → payment_events Exchange → payment_queue 
  → Order Service监听 → 更新order.payment_status = 'paid'
  → Notification Service监听 → 通知Customer和Provider
```

---

### 完整流程总结

```
1. 前端层 (图1-Layer1)
   └─ Customer登录 → 创建订单

2. Gateway层 (图1-Layer2)
   └─ JWT验证 → 限流检查 → 路由转发

3. 微服务层 (图1-Layer3, 图2所有服务)
   ├─ Auth Service: 用户认证
   ├─ Order Service: 订单创建、状态管理
   ├─ Payment Service: 支付处理
   └─ Notification Service: 消息推送

4. 基础设施层 (图1-Layer4)
   ├─ Redis: 限流计数、会话缓存
   └─ RabbitMQ: 事件驱动通信 (图3)
       ├─ 5个Exchange: order_events, payment_events, ...
       ├─ 3个Queue: order_queue, payment_queue, review_queue
       └─ 15+事件: order.created, order.accepted, payment.completed, ...

5. 数据库层 (图1-Layer5, 图4)
   ├─ MySQL (3个实例 - AWS RDS)
   │   ├─ auth_db: 用户认证数据
   │   ├─ order_db: 订单事务数据
   │   └─ payment_db: 支付交易数据
   └─ MongoDB (3个集群 - Atlas)
       ├─ user_db: 用户资料（灵活schema）
       ├─ review_db: 评价数据
       └─ notification_db: 通知消息（追加型）
```

### 技术亮点体现

✅ **微服务解耦（图2）**: 6个服务独立开发、独立部署  
✅ **事件驱动（图3）**: 订单状态变更自动触发通知，无需显式调用  
✅ **多数据库（图4）**: 订单用MySQL保证ACID，通知用MongoDB提升性能  
✅ **API Gateway（图1）**: 统一入口，简化前端调用  
✅ **异步处理（图3）**: 通知推送不阻塞订单创建，提升响应速度

---

## 图5: Customer Publish Order Sequence Diagram（客户发布订单时序图）

### 流程概述
展示Customer从前端发起订单创建请求，经过Gateway认证、Order Service处理、数据库存储、事件发布到最终通知推送的**完整交互流程**。

### 15步详细流程

#### Step 1-2: 前端发起请求
```javascript
// Frontend - Customer点击"发布订单"按钮
POST http://localhost:8080/api/customer/orders/publish
Headers: {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
}
Body: {
  "title": "电脑维修",
  "description": "电脑无法开机，需要检修",
  "service_type": "it_technology",
  "price": 200.00,
  "location": "NORTH",
  "address": "北京市海淀区中关村大街1号"
}
```

**关键点**: 
- Customer已登录，携带JWT Token
- 请求发送到API Gateway的统一入口（8080端口）

---

#### Step 3-4: API Gateway认证
```python
# gateway-service/src/gateway_service/api/routes.py
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request, ...):
    # Step 3: 验证JWT Token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Step 4: 调用Auth Service验证Token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/verify-token",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    user_data = response.json()  # {user_id: 123, role: "customer"}
    
    # 将user_id注入到请求头，转发给Order Service
    request.state.user_id = user_data["user_id"]
```

**关键点**:
- Gateway不直接验证Token，而是调用Auth Service
- 验证成功后提取user_id，注入到后续请求中

---

#### Step 5-6: Order Service创建订单
```python
# services/order-service/src/order_service/services/customer_order_service.py
@staticmethod
async def publish_order(
    db: AsyncSession,
    customer_id: int,  # 来自Gateway注入的user_id
    title: str,
    description: str,
    service_type: str,
    price: float,
    location: str,
    address: str,
    service_start_time: Optional[datetime] = None,
    service_end_time: Optional[datetime] = None,
) -> Order:
    """发布订单 - 状态为 pending_review,等待管理员审核"""
    
    # Step 5: 创建订单对象
    order = await OrderDAO.create_order(
        db=db,
        customer_id=customer_id,
        title=title,
        description=description,
        service_type=ServiceType(service_type),  # ENUM: it_technology
        price=price,
        location=LocationEnum(location),  # ENUM: NORTH
        address=address,
        service_start_time=service_start_time,
        service_end_time=service_end_time,
    )
    # 此时订单状态默认为: OrderStatus.pending_review
    
    # Step 6: 从User Service获取Customer资料（用于后续通知）
    async with httpx.AsyncClient() as client:
        profile = await client.get(
            f"{USER_SERVICE_URL}/customers/{customer_id}/profile"
        )
    
    return order
```

**关键点**:
- 订单初始状态是`pending_review`（需管理员审核）
- 需要调用User Service获取Customer详细信息

---

#### Step 7-8: 数据库持久化
```python
# services/order-service/src/order_service/dao/order_dao.py
@staticmethod
async def create_order(db: AsyncSession, ...) -> Order:
    # Step 7: 创建Order实例
    order = Order(
        customer_id=customer_id,
        title=title,
        description=description,
        service_type=service_type,
        price=price,
        location=location,
        address=address,
        status=OrderStatus.pending_review,  # 默认状态
        payment_status=PaymentStatus.unpaid,  # 未支付
        created_at=datetime.now(UTC),
    )
    
    # Step 8: 插入数据库（图4 - MySQL order_db）
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    return order  # 返回带有id的订单对象
```

**数据库操作（MySQL）**:
```sql
INSERT INTO orders (
    customer_id, title, description, service_type, 
    price, location, address, status, payment_status, created_at
) VALUES (
    123, '电脑维修', '电脑无法开机，需要检修', 'it_technology',
    200.00, 'NORTH', '北京市海淀区中关村大街1号', 'pending_review', 'unpaid', NOW()
);
```

---

#### Step 9-10: 事件发布（图3 - Event-Driven）
```python
# services/order-service/src/order_service/services/customer_order_service.py（续）
    # Step 9: 订单保存成功后，发布事件
    event = OrderCreatedEvent(
        order_id=order.id,  # 数据库生成的订单ID
        customer_id=customer_id,
        title=title,
        price=price,
        location=location,
        timestamp=datetime.now(UTC),
    )
    
    # Step 10: 发送到RabbitMQ
    await EventPublisher.publish_order_created(event)
    
    return order
```

**事件发布代码**:
```python
# services/order-service/src/order_service/events/publishers/event_publisher.py
@staticmethod
async def publish_order_created(event: OrderCreatedEvent):
    message = {
        "order_id": event.order_id,
        "customer_id": event.customer_id,
        "title": event.title,
        "price": event.price,
        "location": event.location,
        "timestamp": event.timestamp.isoformat(),
    }
    
    # 发布到RabbitMQ的order_events Exchange
    await publish_event(
        exchange="order_events",
        routing_key="order.created",  # 路由键
        message=message
    )
```

**RabbitMQ路由（图3）**:
```
Order Service (Producer)
  → order_events Exchange (Topic)
    → Routing Key: "order.created"
      → order_queue (Binding: order.*)
        → Notification Service (Consumer)
```

---

#### Step 11-12: Notification Service处理事件
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py
async def handle_order_created(message: dict):
    """处理订单创建事件"""
    order_id = message['order_id']
    customer_id = message['customer_id']
    location = message['location']
    title = message['title']
    price = message['price']
    
    # Step 11: 缓存通知到Redis（可选，提升性能）
    await redis_client.setex(
        f"notification:order:{order_id}",
        3600,  # 1小时过期
        json.dumps(message)
    )
    
    # Step 12: 查询匹配的Providers（图4 - MongoDB）
    # 条件: 服务区域匹配、技能匹配、已认证
    providers = await db.provider_profiles.find({
        "service_areas": {"$in": [location]},  # 服务区域包含NORTH
        "skills": {"$regex": "电脑|维修|IT", "$options": "i"},  # 技能匹配
        "verified": True,  # 已认证
        "is_active": True  # 账号活跃
    }).to_list(20)  # 最多通知20个Provider
    
    # Step 13: 创建通知记录（图4 - MongoDB）
    notifications = []
    for provider in providers:
        notification = {
            "user_id": provider['user_id'],
            "type": "new_order",
            "title": "新订单通知",
            "content": f"您有一个新的订单: {title}（¥{price}）",
            "order_id": order_id,
            "location": location,
            "is_read": False,
            "created_at": datetime.now(UTC)
        }
        notifications.append(notification)
    
    if notifications:
        await db.provider_inbox.insert_many(notifications)
    
    # 同时通知Customer订单创建成功
    await db.customer_inbox.insert_one({
        "user_id": customer_id,
        "type": "order_created",
        "title": "订单创建成功",
        "content": f"您的订单"{title}"已发布，等待管理员审核",
        "order_id": order_id,
        "is_read": False,
        "created_at": datetime.now(UTC)
    })
```

---

#### Step 13-14: 返回响应
```python
# Step 13: Order Service返回订单数据给Gateway
return {
    "order_id": order.id,
    "status": "pending_review",
    "message": "订单创建成功，等待审核"
}

# Step 14: Gateway返回给Frontend
# Step 15: Frontend显示成功消息
```

**前端展示**:
```javascript
// Frontend收到响应
{
    "order_id": 789,
    "status": "pending_review",
    "message": "订单创建成功，等待审核"
}

// 弹出提示
alert("订单发布成功！订单号: #789");
// 跳转到订单列表页面
router.push('/customer/orders');
```

---

### 流程总结

```
1. Customer → Frontend → POST /api/customer/orders/publish
2. Frontend → API Gateway (JWT Token验证)
3. API Gateway → Auth Service (验证Token)
4. Auth Service → API Gateway (返回user_id)
5. API Gateway → Order Service (转发请求 + user_id)
6. Order Service → User Service (获取Customer资料)
7. User Service → Order Service (返回资料)
8. Order Service → MySQL (插入订单记录)
9. MySQL → Order Service (返回order_id)
10. Order Service → RabbitMQ (发布order.created事件)
11. RabbitMQ → Notification Service (路由事件)
12. Notification Service → Redis (缓存通知)
13. Notification Service → MongoDB (插入通知记录)
14. Order Service → API Gateway (返回成功响应)
15. API Gateway → Frontend (返回订单信息)
```

### 关键技术点

✅ **JWT认证**: Gateway统一验证，避免每个服务重复认证  
✅ **同步+异步**: 订单创建是同步（立即返回），通知推送是异步（后台处理）  
✅ **事件驱动**: Order Service不直接调用Notification Service，通过事件解耦  
✅ **数据库选型**: 订单用MySQL（ACID），通知用MongoDB（高并发写入）  
✅ **智能匹配**: Notification Service根据location和skills智能匹配Providers

---

## 图6: Provider Accept Order Sequence Diagram（服务商接受订单时序图）

### 流程概述
展示Provider从通知列表看到新订单，点击接单后，系统如何更新订单状态、验证权限、发布事件并通知双方的**完整交互流程**。

### 15步详细流程

#### Step 1-2: Provider发起接单请求
```javascript
// Frontend - Provider在"可接订单"列表中点击"接单"
PUT http://localhost:8080/api/provider/orders/789/accept
Headers: {
  "Authorization": "Bearer <provider_token>"
}
```

**前置条件**:
- Provider已登录（role = 'provider'）
- 订单状态必须是`pending`（已通过管理员审核）

---

#### Step 3-4: API Gateway认证
```python
# gateway-service/src/gateway_service/api/routes.py
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request, ...):
    # Step 3: 验证JWT Token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Step 4: 验证Token并检查角色
    user_data = await verify_token_with_auth_service(token)
    
    # 检查是否为Provider角色
    if user_data["role"] != "provider":
        raise HTTPException(
            status_code=403, 
            detail="Only providers can accept orders"
        )
    
    # 注入provider_id
    request.state.user_id = user_data["user_id"]
    request.state.role = user_data["role"]
```

---

#### Step 5: Order Service处理接单请求
```python
# services/order-service/src/order_service/services/provider_order_service.py
@staticmethod
async def accept_order(db: AsyncSession, provider_id: int, order_id: int) -> Order:
    """接受订单"""
    
    # Step 5: 查询订单
    order = await OrderDAO.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    # 验证订单状态（只能接受pending状态的订单）
    if order.status != OrderStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The order has already been accepted!"
        )
    
    # Step 6: 检查订单状态（从DB读取）
    # 确保订单没有被其他Provider抢先接单
    return order
```

---

#### Step 6-7: 验证并更新订单
```python
# services/order-service/src/order_service/dao/order_dao.py
@staticmethod
async def accept_order(db: AsyncSession, order_id: int, provider_id: int) -> Order:
    """接受订单 - 原子操作"""
    
    # Step 7: 更新订单（MySQL事务保证）
    result = await db.execute(
        update(Order)
        .where(Order.id == order_id)
        .where(Order.status == OrderStatus.pending)  # 乐观锁
        .values(
            provider_id=provider_id,
            status=OrderStatus.accepted,
            updated_at=datetime.now(UTC)
        )
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=400,
            detail="Order has been accepted by another provider"
        )
    
    await db.commit()
    
    # 重新查询订单
    order = await db.get(Order, order_id)
    return order
```

**SQL操作（MySQL - 图4）**:
```sql
-- 原子更新（WHERE确保只更新pending状态）
UPDATE orders 
SET 
    provider_id = 456,  -- Provider李四
    status = 'accepted',
    updated_at = NOW()
WHERE 
    id = 789 
    AND status = 'pending';  -- 乐观锁：只有pending才能更新

-- 如果rowcount = 0，说明订单已被其他Provider接单
```

---

#### Step 8-9: 发布订单接受事件
```python
# services/order-service/src/order_service/services/provider_order_service.py（续）
    # Step 8: 订单更新成功
    updated_order = await OrderDAO.accept_order(db, order_id, provider_id)
    
    # Step 9: 发布order.accepted事件（图3）
    event = OrderAcceptedEvent(
        order_id=order_id,
        customer_id=order.customer_id,  # Customer张三
        provider_id=provider_id,  # Provider李四
        timestamp=datetime.now(UTC)
    )
    await EventPublisher.publish_order_accepted(event)
    
    return updated_order
```

**事件发布**:
```python
# services/order-service/src/order_service/events/publishers/event_publisher.py
@staticmethod
async def publish_order_accepted(event: OrderAcceptedEvent):
    message = {
        "order_id": event.order_id,
        "customer_id": event.customer_id,
        "provider_id": event.provider_id,
        "timestamp": event.timestamp.isoformat(),
    }
    
    await publish_event(
        exchange="order_events",
        routing_key="order.accepted",
        message=message
    )
```

---

#### Step 10-11: Notification Service处理事件
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py
async def handle_order_accepted(message: dict):
    """处理订单接受事件"""
    order_id = message['order_id']
    customer_id = message['customer_id']
    provider_id = message['provider_id']
    
    # Step 10: 发送order.accepted事件到Notification Service
    
    # Step 11: 缓存通知到Redis
    await redis_client.setex(
        f"notification:order:accepted:{order_id}",
        3600,
        json.dumps(message)
    )
    
    # Step 12: 创建通知（图4 - MongoDB）
    
    # 通知Customer
    customer_notification = {
        "user_id": customer_id,
        "type": "order_accepted",
        "title": "订单已被接受",
        "content": "您的订单已被服务商接受，请及时支付",
        "order_id": order_id,
        "provider_id": provider_id,
        "is_read": False,
        "created_at": datetime.now(UTC)
    }
    await db.customer_inbox.insert_one(customer_notification)
    
    # 通知Provider
    provider_notification = {
        "user_id": provider_id,
        "type": "order_accepted",
        "title": "接单成功",
        "content": "您已成功接单，请等待客户支付",
        "order_id": order_id,
        "customer_id": customer_id,
        "is_read": False,
        "created_at": datetime.now(UTC)
    }
    await db.provider_inbox.insert_one(provider_notification)
```

**MongoDB插入（图4）**:
```javascript
// customer_inbox集合
{
    user_id: 123,  // Customer张三
    type: "order_accepted",
    title: "订单已被接受",
    content: "您的订单已被服务商接受，请及时支付",
    order_id: 789,
    provider_id: 456,
    is_read: false,
    created_at: ISODate("2025-10-25T12:00:00Z")
}

// provider_inbox集合
{
    user_id: 456,  // Provider李四
    type: "order_accepted",
    title: "接单成功",
    content: "您已成功接单，请等待客户支付",
    order_id: 789,
    customer_id: 123,
    is_read: false,
    created_at: ISODate("2025-10-25T12:00:00Z")
}
```

---

#### Step 13-15: 返回响应
```python
# Step 13: Order Service返回更新后的订单
return {
    "order_id": order.id,
    "status": "accepted",
    "provider_id": provider_id,
    "message": "接单成功"
}

# Step 14: API Gateway转发响应
# Step 15: Frontend显示成功消息
```

**前端展示**:
```javascript
// Provider端
{
    "order_id": 789,
    "status": "accepted",
    "provider_id": 456,
    "message": "接单成功"
}

// 弹出提示
alert("接单成功！请等待客户支付");
// 跳转到"我的订单"页面
router.push('/provider/my-orders');
```

---

### 流程总结

```
1. Provider → Frontend → PUT /api/provider/orders/789/accept
2. Frontend → API Gateway (JWT Token验证)
3. API Gateway → Auth Service (验证Token + 角色检查)
4. Auth Service → API Gateway (返回provider_id + role)
5. API Gateway → Order Service (转发请求 + provider_id)
6. Order Service → MySQL (查询订单状态)
7. MySQL → Order Service (返回订单: status=pending)
8. Order Service → MySQL (原子更新: provider_id + status=accepted)
9. MySQL → Order Service (更新成功确认)
10. Order Service → RabbitMQ (发布order.accepted事件)
11. RabbitMQ → Notification Service (路由事件)
12. Notification Service → Redis (缓存通知)
13. Notification Service → MongoDB (插入双方通知)
14. Order Service → API Gateway (返回成功响应)
15. API Gateway → Frontend (返回订单信息)
```

### 关键技术点

✅ **乐观锁**: 使用`WHERE status = 'pending'`防止重复接单  
✅ **原子操作**: MySQL事务保证provider_id和status同时更新  
✅ **角色验证**: Gateway检查JWT中的role，只有Provider可接单  
✅ **事件通知**: 接单成功自动通知Customer和Provider双方  
✅ **幂等性**: 如果订单已被接受，返回400错误而非500

---

### 两张时序图的对比

| 对比项 | Customer发布订单 | Provider接受订单 |
|--------|-----------------|-----------------|
| **触发角色** | Customer | Provider |
| **核心操作** | 创建订单（INSERT） | 更新订单（UPDATE） |
| **初始状态** | 无 → pending_review | pending → accepted |
| **并发问题** | 无（新建订单） | 有（多Provider抢单） |
| **解决方案** | 无需特殊处理 | 乐观锁（WHERE status = 'pending'） |
| **事件发布** | order.created | order.accepted |
| **通知对象** | 匹配的Providers（批量） | Customer + Provider（双向） |
| **数据库操作** | MySQL INSERT + MongoDB批量插入 | MySQL UPDATE + MongoDB双记录插入 |
| **业务复杂度** | 中等（需查询User资料） | 较高（需防止重复接单） |

---

### Presentation Tips（时序图讲解）

**讲解顺序**:
1. **先讲图5（发布订单）**: 流程简单，从用户角度更好理解
2. **再讲图6（接受订单）**: 重点讲解并发控制和乐观锁
3. **对比两张图**: 强调INSERT vs UPDATE、单向通知 vs 双向通知

**关键演示点**:
- **图5重点**: 展示事件驱动如何智能匹配Providers
- **图6重点**: 展示MySQL乐观锁如何防止重复接单
- **代码演示**: 
  - `customer_order_service.py` 的 `publish_order` 方法
  - `provider_order_service.py` 的 `accept_order` 方法
  - `order_event_handler.py` 的事件处理逻辑

**可能的问题**:
**Q: 如果两个Provider同时点击接单怎么办？**  
A: MySQL的`WHERE status = 'pending'`乐观锁保证只有一个UPDATE成功，另一个返回rowcount=0并抛出400错误。

**Q: 如果RabbitMQ宕机，通知会丢失吗？**  
A: RabbitMQ设置了`durable=True`和`delivery_mode=2`，消息会持久化到磁盘，重启后自动恢复。

**Q: 为什么不用Redis存储订单，而用MySQL？**  
A: 订单是核心业务数据，需要ACID事务保证（防止金额错误、状态不一致），Redis只做缓存和限流。

---

## 图7: Logical Detail Deployment Diagram（逻辑部署详图）

### 部署架构概述

本图采用**UML部署图（Deployment Diagram）**标准，展示系统各组件在物理/虚拟环境中的部署拓扑，重点说明"**什么组件部署在哪里**"，而非内部实现细节。

### UML Stereotypes（构造型）说明

在UML部署图中，使用构造型（Stereotype）来标识不同类型的部署元素：

| Stereotype | 中文含义 | 说明 | 图中示例 |
|-----------|---------|------|---------|
| `<<location>>` | 部署位置/网络区域 | 表示网络边界或逻辑区域 | Internet, AWS Cloud |
| `<<execution environment>>` | 执行环境 | 表示运行软件的环境容器 | Frontend Server, Microservices Cluster |
| `<<device>>` | 物理设备 | 表示客户端硬件设备 | Client PC |
| `<<artifact>>` | 软件制品 | 表示可部署的软件包/JAR/WAR | gateway-service.jar, Frontend UI |
| `<<database>>` | 数据库实例 | 表示数据库服务器 | auth_db (MySQL), user_db (MongoDB) |
| `<<node>>` | 基础设施节点 | 表示中间件或基础设施服务 | RabbitMQ, Redis |

### 部署层次结构

#### **1️⃣ Internet层（<<location>>）**

**部署元素**:
- **Client PC (<<device>>)**: 用户通过浏览器访问系统
  - **Browser**: Chrome, Safari, Firefox
  - **Protocol**: HTTPS (443端口)
  - **Connection**: 通过Internet访问AWS Cloud中的Frontend UI

**说明**: 这是系统的外部边界，代表所有互联网用户的访问入口。

---

#### **2️⃣ AWS Cloud层（<<location>>）**

这是系统的核心部署区域，包含所有应用服务器、中间件和数据库。

##### **Frontend Server (<<execution environment>>)**

**部署制品**: `Frontend UI (Vue.js + Vite)`  
**端口**: 80 (HTTP), 443 (HTTPS)  
**技术栈**: 
- Vue.js 3 (前端框架)
- Vite (构建工具)
- Nginx (Web服务器，用于提供静态文件)

**代码位置**: `frontend/src/`

**职责**:
- 提供三种角色的Web界面（Customer, Provider, Admin）
- 静态资源托管（HTML, CSS, JS, Images）
- 通过AJAX调用API Gateway

**实际部署方式**:
```bash
# 构建前端
cd frontend
npm run build  # 生成 dist/ 目录

# 部署到Nginx
# dist/ 目录内容 → /var/www/html/
# Nginx配置 → /etc/nginx/sites-available/frontend.conf
```

---

##### **API Gateway (<<execution environment>>)**

**部署制品**: `gateway-service.jar (FastAPI)`  
**端口**: 8080  
**技术栈**: FastAPI (Python) + Uvicorn (ASGI服务器)

**核心组件**:
- **Router**: 路由转发逻辑
- **JWT Handler**: Token验证
- **Rate Limiter**: 基于Redis的限流
- **Middleware**: CORS、日志、异常处理

**代码位置**: `gateway-service/src/gateway_service/`

**职责**:
- 统一API入口（所有前端请求经过这里）
- JWT认证（验证用户身份和权限）
- 路由转发（将请求路由到对应的微服务）
- 限流保护（防止恶意攻击）

**实际部署命令**:
```bash
cd gateway-service
uvicorn gateway_service.main:app --host 0.0.0.0 --port 8080 --app-dir src
```

---

##### **Microservices Cluster (<<execution environment>>)**

6个独立部署的微服务，每个都是一个**独立的FastAPI应用**：

| Service | Artifact | Port | Database | Technology | Code Path |
|---------|----------|------|----------|------------|-----------|
| **Auth Service** | auth-service.jar | 8000 | MySQL (auth_db) | FastAPI + SQLAlchemy | `services/auth-service/src/` |
| **User Service** | user-service.jar | 8002 | MongoDB (user_db) | FastAPI + Motor | `services/user-service/src/` |
| **Order Service** | order-service.jar | 8003 | MySQL (order_db) | FastAPI + SQLAlchemy | `services/order-service/src/` |
| **Payment Service** | payment-service.jar | 8004 | MySQL (payment_db) | FastAPI + SQLAlchemy | `services/payment-service/src/` |
| **Review Service** | review-service.jar | 8005 | MongoDB (review_db) | FastAPI + Motor | `services/review-service/src/` |
| **Notification Service** | notification-service.jar | 8006 | MongoDB (notification_db) | FastAPI + Motor | `services/notification-service/src/` |

**部署特点**:
- ✅ **独立部署**: 每个服务可单独启动/停止/更新
- ✅ **独立数据库**: 每个服务有自己的数据库（Database per Service模式）
- ✅ **无状态**: 所有服务都是无状态的，便于水平扩展
- ✅ **端口隔离**: 每个服务监听不同端口，避免冲突

**实际部署示例（Order Service）**:
```bash
cd services/order-service
uvicorn order_service.main:app --reload --host 0.0.0.0 --port 8003 --app-dir src
```

---

##### **Infrastructure Layer（基础设施层）**

###### **RabbitMQ (<<node>>)**

**技术**: RabbitMQ 3.x (Message Broker)  
**端口**: 
- 5672 (AMQP协议，应用连接)
- 15672 (Management UI，管理界面)

**职责**:
- **消息队列**: 实现异步事件通信
- **Exchange类型**: Topic Exchange（支持灵活路由）
- **Exchanges**: 
  - `order_events` (订单事件)
  - `payment_events` (支付事件)
  - `review_events` (评价事件)
  - `auth_events` (认证事件)
  - `user_events` (用户事件)

**Consumers（消费者）**: 
- Notification Service 订阅所有队列，接收事件后发送通知

**配置位置**: `infrastructure/rabbitmq/definitions.json`

**实际部署**:
```bash
# Docker方式
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -v ./infrastructure/rabbitmq:/etc/rabbitmq \
  rabbitmq:3-management
```

---

###### **Redis (<<node>>)**

**技术**: Redis 7.x (In-Memory Cache)  
**端口**: 6379

**用途**:
1. **Rate Limiting（限流）**: API Gateway使用Redis计数器
   - Key格式: `rate_limit:{user_id}:{endpoint}`
   - 过期时间: 60秒
   
2. **Session Cache（会话缓存）**: 
   - JWT Token黑名单
   - 用户权限缓存
   
3. **Notification Cache（通知缓存）**:
   - 未读通知数量统计
   - 最近通知快速查询

**代码示例**:
```python
# gateway-service/src/gateway_service/core/rate_limiter.py
async def check_rate_limit(user_id: int, endpoint: str):
    key = f"rate_limit:{user_id}:{endpoint}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)  # 60秒窗口
    return count <= 100  # 每分钟最多100次请求
```

**实际部署**:
```bash
# Docker方式
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

---

##### **Database Layer（数据库层）**

###### **MySQL 8.0 (<<database>>) - AWS RDS Multi-AZ**

**部署方式**: AWS RDS（托管数据库服务）  
**高可用**: Multi-AZ（双可用区，自动故障转移）  
**备份**: 自动备份（保留7天）

**数据库实例**:

| Database | 服务 | 表结构 | 连接字符串示例 |
|----------|------|--------|---------------|
| **auth_db** | Auth Service | `users`, `roles` | `mysql+aiomysql://user:pass@auth-db.rds.amazonaws.com:3306/auth_db` |
| **order_db** | Order Service | `orders` | `mysql+aiomysql://user:pass@order-db.rds.amazonaws.com:3306/order_db` |
| **payment_db** | Payment Service | `payments`, `refunds` | `mysql+aiomysql://user:pass@payment-db.rds.amazonaws.com:3306/payment_db` |

**为什么选择MySQL？**
- ✅ **ACID事务**: 订单、支付、认证需要强一致性
- ✅ **外键约束**: 保证数据完整性（如user_id必须存在）
- ✅ **复杂查询**: 支持JOIN、子查询、聚合函数
- ✅ **成熟生态**: SQLAlchemy ORM、Alembic迁移工具

**实际连接代码**:
```python
# services/auth-service/src/auth_service/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "mysql+aiomysql://user:pass@auth-db.rds.amazonaws.com:3306/auth_db",
    pool_size=10,
    max_overflow=20
)
```

---

###### **MongoDB 7.0 (<<database>>) - MongoDB Atlas**

**部署方式**: MongoDB Atlas（云托管服务）  
**高可用**: 3-node Replica Set（3节点副本集）  
**备份**: Continuous Backup（持续备份，可恢复到任意时间点）

**数据库实例**:

| Database | 服务 | 集合 | 连接字符串示例 |
|----------|------|------|---------------|
| **user_db** | User Service | `customer_profiles`, `provider_profiles` | `mongodb+srv://user:pass@user-cluster.mongodb.net/user_db` |
| **review_db** | Review Service | `reviews`, `ratings` | `mongodb+srv://user:pass@review-cluster.mongodb.net/review_db` |
| **notification_db** | Notification Service | `customer_inbox`, `provider_inbox` | `mongodb+srv://user:pass@notification-cluster.mongodb.net/notification_db` |

**为什么选择MongoDB？**
- ✅ **灵活Schema**: 用户资料可随时扩展字段（skills, portfolios）
- ✅ **嵌套文档**: Provider的可用时间表可用嵌套对象存储
- ✅ **高并发写入**: 通知服务需要频繁插入消息
- ✅ **全文搜索**: Review内容支持文本搜索

**实际连接代码**:
```python
# services/user-service/src/user_service/core/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    "mongodb+srv://user:pass@user-cluster.mongodb.net/",
    maxPoolSize=50
)
db = client["user_db"]
```

---

### 通信模式详解

| 连接类型 | 图中表示 | 说明 | 示例 |
|---------|---------|------|------|
| **实线箭头** `---` | 同步HTTP调用 | 请求-响应模式，等待结果 | Client → Frontend, Gateway → Services, Services → Database |
| **虚线箭头** `-.->` | 部署关系/缓存访问 | 表示"部署在"或"使用" | Services -.-> Redis (使用缓存) |
| **粗箭头** `==>` | 异步消息通信 | 通过RabbitMQ发布事件 | Services ==> RabbitMQ ==> Notification |

**同步调用示例（HTTP）**:
```
Frontend → API Gateway → Order Service → MySQL
  (HTTPS)     (HTTP)          (SQL)
```

**异步通信示例（Events）**:
```
Order Service → RabbitMQ (order.created) → Notification Service
    (Publish)        (Route)              (Consume + Send Email)
```

---

### 部署架构特点

#### **1️⃣ 架构风格**: Microservices（微服务架构）
- 7个独立服务（1 Gateway + 6 Microservices）
- 每个服务独立部署、独立扩展
- 服务间通过REST API和消息队列通信

#### **2️⃣ 通信方式**: 
- **同步**: REST API (HTTP/JSON) - 用于查询和即时操作
- **异步**: Event-Driven (RabbitMQ) - 用于通知和解耦

#### **3️⃣ 数据策略**: Polyglot Persistence（多语言持久化）
- **MySQL**: 事务性数据（Auth, Order, Payment）
- **MongoDB**: 灵活schema数据（User, Review, Notification）

#### **4️⃣ 云平台**: 
- **AWS RDS**: MySQL托管服务（Multi-AZ高可用）
- **MongoDB Atlas**: MongoDB云服务（Replica Set）
- **AWS EC2/ECS**: 应用服务器（可选Kubernetes）

#### **5️⃣ 高可用设计**:
- **MySQL**: Multi-AZ双可用区，自动故障转移
- **MongoDB**: 3-node Replica Set，主从自动切换
- **RabbitMQ**: 消息持久化（durable=True）
- **Services**: 无状态设计，可水平扩展（添加更多实例）

#### **6️⃣ 缓存策略**:
- **Redis**: 统一缓存层
  - Rate Limiting（限流计数）
  - Session Cache（会话缓存）
  - Notification Cache（通知缓存）

---

### 关键设计决策

#### **1️⃣ API Gateway模式**
**决策**: 使用单一网关作为统一入口  
**优点**:
- ✅ 简化客户端调用（只需知道一个地址）
- ✅ 集中认证和授权（JWT验证统一处理）
- ✅ 流量控制和限流（防止恶意攻击）
- ✅ 服务发现和路由（客户端无需知道服务地址）

**代码体现**:
```python
# gateway-service/src/gateway_service/api/routes.py
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(path: str, request: Request):
    # 1. JWT验证
    # 2. 限流检查
    # 3. 路由转发到对应服务
```

---

#### **2️⃣ Database per Service（每服务一数据库）**
**决策**: 每个微服务拥有独立的数据库  
**优点**:
- ✅ 避免服务间耦合（改一个服务的表不影响其他服务）
- ✅ 独立扩展（订单服务可单独升级数据库性能）
- ✅ 故障隔离（Auth DB宕机不影响Review服务）

**实施**:
- Auth Service → `auth_db` (MySQL)
- User Service → `user_db` (MongoDB)
- Order Service → `order_db` (MySQL)
- Payment Service → `payment_db` (MySQL)
- Review Service → `review_db` (MongoDB)
- Notification Service → `notification_db` (MongoDB)

---

#### **3️⃣ Event-Driven Architecture（事件驱动架构）**
**决策**: 使用RabbitMQ实现服务间异步通信  
**优点**:
- ✅ 解耦服务依赖（Order Service不需要知道Notification Service的地址）
- ✅ 异步处理（发布订单后立即返回，通知异步发送）
- ✅ 可扩展性（新增Consumer无需修改Producer）
- ✅ 故障容错（消息队列缓冲，Consumer暂时宕机不丢消息）

**实际场景**:
```
订单创建流程:
1. Order Service → MySQL (保存订单)
2. Order Service → RabbitMQ (发布order.created事件)
3. RabbitMQ → Notification Service (异步消费)
4. Notification Service → MongoDB (插入通知)
5. Notification Service → Email/SMS (发送邮件/短信)
```

---

#### **4️⃣ Polyglot Persistence（多语言持久化）**
**决策**: 根据数据特性选择不同数据库  
**MySQL使用场景**:
- **Auth Service**: 用户认证需要ACID事务（密码错误会锁账户）
- **Order Service**: 订单状态流转需要强一致性（不能出现幻读）
- **Payment Service**: 金融交易必须精确（DECIMAL类型 + 事务）

**MongoDB使用场景**:
- **User Service**: 用户资料灵活扩展（Provider的技能列表长度不固定）
- **Review Service**: 评论内容非结构化（全文搜索需求）
- **Notification Service**: 高并发写入（每天数万条通知）

---

#### **5️⃣ Stateless Services（无状态服务）**
**决策**: 所有微服务不保存会话状态  
**优点**:
- ✅ 水平扩展（可随时添加更多服务实例）
- ✅ 负载均衡（任意实例都可处理请求）
- ✅ 容错性强（某个实例宕机不影响用户会话）

**实现方式**:
- JWT Token存储用户信息（无需服务器端Session）
- Redis存储共享状态（限流计数、黑名单）

---

#### **6️⃣ Centralized Cache（集中式缓存）**
**决策**: 使用Redis作为统一缓存层  
**优点**:
- ✅ 性能提升（热点数据缓存，减少DB查询）
- ✅ 限流保护（基于Redis计数器实现）
- ✅ 跨服务共享（多个服务共用一个Redis）

**使用场景**:
```python
# 限流示例
key = f"rate_limit:{user_id}"
count = await redis.incr(key)
if count == 1:
    await redis.expire(key, 60)
if count > 100:
    raise HTTPException(429, "Too Many Requests")
```

---

### 实际部署脚本

#### **本地开发环境启动**:
```bash
# 1. 启动基础设施
cd infrastructure
docker-compose up -d mysql mongodb rabbitmq redis

# 2. 启动所有服务
cd ..
./scripts/start-services.sh

# 包含以下命令:
# - uvicorn auth_service.main:app --port 8000 --app-dir src &
# - uvicorn user_service.main:app --port 8002 --app-dir src &
# - uvicorn order_service.main:app --port 8003 --app-dir src &
# - uvicorn payment_service.main:app --port 8004 --app-dir src &
# - uvicorn review_service.main:app --port 8005 --app-dir src &
# - uvicorn notification_service.main:app --port 8006 --app-dir src &
# - uvicorn gateway_service.main:app --port 8080 --app-dir src &

# 3. 启动前端
cd frontend
npm run dev  # 开发环境
# 或
npm run build && nginx  # 生产环境
```

#### **Kubernetes部署示例**:
```bash
# 1. 部署MySQL StatefulSet
kubectl apply -f infrastructure/kubernetes/mysql/

# 2. 部署MongoDB StatefulSet
kubectl apply -f infrastructure/kubernetes/mongodb/

# 3. 部署RabbitMQ
kubectl apply -f infrastructure/kubernetes/rabbitmq/

# 4. 部署Redis
kubectl apply -f infrastructure/kubernetes/redis/

# 5. 部署微服务
kubectl apply -f infrastructure/kubernetes/auth-service/
kubectl apply -f infrastructure/kubernetes/user-service/
kubectl apply -f infrastructure/kubernetes/order-service/
kubectl apply -f infrastructure/kubernetes/payment-service/
kubectl apply -f infrastructure/kubernetes/review-service/
kubectl apply -f infrastructure/kubernetes/notification-service/
kubectl apply -f infrastructure/kubernetes/gateway-service/
```

---

### Presentation Tips（部署图讲解）

**讲解顺序**:
1. **从外到内**: Internet → AWS Cloud → Services → Databases
2. **从上到下**: Client → Frontend → Gateway → Microservices → Infrastructure → Databases
3. **分层讲解**: 先讲5大层次，再深入每层细节

**关键演示点**:
- **UML Stereotypes**: 解释`<<location>>`, `<<artifact>>`, `<<database>>`等符号的含义
- **通信模式**: 
  - 实线箭头（同步HTTP）
  - 虚线箭头（部署关系/缓存）
  - 粗箭头（异步消息）
- **高可用设计**: 
  - MySQL Multi-AZ自动故障转移
  - MongoDB 3-node Replica Set
  - 微服务无状态，可水平扩展
- **数据库选型**: 
  - MySQL用于事务（Auth, Order, Payment）
  - MongoDB用于灵活schema（User, Review, Notification）

**代码演示**:
```bash
# 演示本地启动所有服务
./scripts/start-services.sh

# 演示查看运行状态
ps aux | grep uvicorn
netstat -an | grep LISTEN | grep -E '800[0-6]|8080'

# 演示访问服务
curl http://localhost:8080/health  # Gateway健康检查
curl http://localhost:8000/health  # Auth Service健康检查
```

**可能的问题**:

**Q1: 为什么需要API Gateway，直接让前端调用各个服务不行吗？**  
A: 
- ❌ 没有Gateway：前端需要知道7个服务的地址，每个请求都要自己加JWT Header
- ✅ 有Gateway：前端只需知道一个地址（8080），Gateway统一处理认证和路由
- 另外，Gateway可以做限流保护，防止恶意攻击

**Q2: 6个微服务用6个数据库，会不会太复杂？**  
A:
- 这是**Database per Service**模式，微服务架构的最佳实践
- 优点：每个服务可以独立选择最适合的数据库（MySQL vs MongoDB）
- 优点：改一个服务的表结构不会影响其他服务
- 缺点：无法使用跨数据库JOIN，需要通过API调用或事件

**Q3: 如果Order Service需要User信息，但它们在不同数据库，怎么查询？**  
A:
- **方式1（推荐）**: Order Service通过HTTP调用User Service的API
  ```python
  user_data = await http_client.get(f"http://user-service:8002/users/{user_id}")
  ```
- **方式2**: Order Service订阅User Service的事件，维护本地缓存
- **方式3**: 使用API Gateway聚合多个服务的数据（BFF模式）

**Q4: RabbitMQ和Redis都是中间件，为什么需要两个？**  
A:
- **RabbitMQ**: 消息队列，用于**异步事件通信**（解耦服务依赖）
  - 示例：Order创建后，异步通知Notification Service发邮件
- **Redis**: 内存缓存，用于**性能优化和限流**
  - 示例：缓存用户权限、限流计数器、热点数据
- 两者职责不同，不可替代

**Q5: 如果要部署到Kubernetes，需要改代码吗？**  
A:
- **代码无需改动**（FastAPI应用是容器化友好的）
- **只需添加**：
  1. Dockerfile（每个服务一个）
  2. Kubernetes YAML（Deployment + Service + ConfigMap）
  3. Ingress配置（替代API Gateway的部分功能）
- 本项目已提供K8s配置：`infrastructure/kubernetes/`

**Q6: 为什么MySQL用AWS RDS，MongoDB用Atlas，而不是自己搭建？**  
A:
- **托管服务优点**：
  - ✅ 自动备份（AWS RDS每天备份，保留7天）
  - ✅ 自动故障转移（Multi-AZ，几秒内切换）
  - ✅ 自动扩展（存储空间不够自动扩容）
  - ✅ 监控和告警（CloudWatch集成）
- **自建数据库缺点**：
  - ❌ 需要自己做备份脚本
  - ❌ 需要自己监控磁盘空间
  - ❌ 宕机需要手动切换主从
- **成本对比**：对于生产环境，托管服务反而更便宜（算上运维人力成本）

---

### 与其他架构图的关联

| 图表 | 关联点 | 说明 |
|------|-------|------|
| **图1: Logical Architecture** | 逻辑架构的物理映射 | Logical Architecture展示5层逻辑结构，Deployment Diagram展示这5层如何部署在实际环境中 |
| **图2: DDD Diagram** | 服务边界的物理体现 | DDD的每个Bounded Context（服务）对应Deployment中的一个Artifact（JAR包） |
| **图3: Event-Driven** | RabbitMQ的物理部署 | Event-Driven图中的Exchange和Queue，在Deployment中体现为RabbitMQ节点 |
| **图4: Polyglot Persistence** | 数据库的物理位置 | Polyglot图中的MySQL/MongoDB，在Deployment中展示为AWS RDS和MongoDB Atlas |
| **图5/图6: Sequence Diagrams** | 交互流程的物理路径 | Sequence中的服务调用，在Deployment中对应实线箭头（HTTP）和粗箭头（Events） |

**综合讲解建议**:
1. **先讲图1（Logical Architecture）**: 建立逻辑层次概念
2. **再讲图7（Deployment Diagram）**: 展示逻辑如何映射到物理
3. **对比两图**: 强调"逻辑架构设计 → 物理部署实现"的演进过程

---

**文档版本**: v4.0  
**最后更新**: 2025-10-25  
**适用场景**: 技术分享、架构评审、新人培训、Pre演示  
**包含图表**: 7张（Logical Architecture, DDD, Event-Driven, Polyglot Persistence, Customer Publish Order Sequence, Provider Accept Order Sequence, Logical Detail Deployment）
