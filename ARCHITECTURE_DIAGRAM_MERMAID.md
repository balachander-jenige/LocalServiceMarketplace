# 优化后的系统架构图 (Mermaid)

## 简化的逻辑架构图（推荐使用）

```mermaid
graph TB
    subgraph Frontend["Frontend Layer"]
        Web["Web Applications<br/>(Vue.js)<br/>Customer | Provider | Admin"]
    end

    subgraph Gateway["API Gateway Layer"]
        GW["API Gateway<br/>(FastAPI)<br/>Auth • Rate Limit • Routing"]
    end

    subgraph Services["Microservices Layer"]
        Auth["Auth Service<br/>(FastAPI + MySQL)"]
        User["User Service<br/>(FastAPI + MongoDB)"]
        Order["Order Service<br/>(FastAPI + MySQL)"]
        Payment["Payment Service<br/>(FastAPI + MySQL)"]
        Review["Review Service<br/>(FastAPI + MongoDB)"]
        Notification["Notification Service<br/>(FastAPI + MongoDB)"]
    end

    subgraph Infrastructure["Infrastructure Layer"]
        MQ["Message Queue<br/>(RabbitMQ)"]
        Cache["Cache<br/>(Redis)"]
    end

    subgraph Database["Database Layer"]
        MySQL[("MySQL<br/>Auth | Order | Payment")]
        MongoDB[("MongoDB<br/>User | Review | Notification")]
    end

    %% Connections
    Web -->|REST API| GW
    GW --> Auth
    GW --> User
    GW --> Order
    GW --> Payment
    GW --> Review
    GW --> Notification

    %% Service to Database
    Auth --> MySQL
    Order --> MySQL
    Payment --> MySQL
    User --> MongoDB
    Review --> MongoDB
    Notification --> MongoDB

    %% Service to Infrastructure
    Auth -.->|Cache| Cache
    User -.->|Cache| Cache
    Order ==>|Publish| MQ
    Payment ==>|Publish| MQ
    Review ==>|Publish| MQ
    MQ ==>|Subscribe| Notification

    %% Service to Service
    User -.->|Verify| Auth
    Order -.->|Get User| User
    Payment -.->|Get Order| Order

    %% Styling
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef gateway fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef service fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef infra fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef database fill:#fbe9e7,stroke:#d84315,stroke-width:2px

    class Web frontend
    class GW gateway
    class Auth,User,Order,Payment,Review,Notification service
    class MQ,Cache infra
    class MySQL,MongoDB database
```

---

## Logical Detail Deployment Diagram（逻辑部署详图）

### 微服务部署架构视图

```mermaid
graph TB
    subgraph Internet["<<location>> Internet"]
        ClientPC["<<device>><br/>Client PC"]
    end

    subgraph AWS["<<location>> AWS Cloud"]
        subgraph Frontend["<<execution environment>><br/>Frontend Server"]
            FrontendUI["<<artifact>><br/>Frontend UI<br/>(Vue.js + Vite)"]
        end

        subgraph Gateway["<<execution environment>><br/>API Gateway"]
            GatewayService["<<artifact>><br/>gateway-service.jar<br/>(FastAPI)<br/>Port: 8080"]
        end

        subgraph Services["<<execution environment>><br/>Microservices Cluster"]
            AuthService["<<artifact>><br/>auth-service.jar<br/>Port: 8000"]
            UserService["<<artifact>><br/>user-service.jar<br/>Port: 8002"]
            OrderService["<<artifact>><br/>order-service.jar<br/>Port: 8003"]
            PaymentService["<<artifact>><br/>payment-service.jar<br/>Port: 8004"]
            ReviewService["<<artifact>><br/>review-service.jar<br/>Port: 8005"]
            NotificationService["<<artifact>><br/>notification-service.jar<br/>Port: 8006"]
        end

        subgraph Infrastructure["Infrastructure"]
            RabbitMQ["<<node>><br/>RabbitMQ<br/>Message Queue"]
            Redis["<<node>><br/>Redis<br/>Cache Server"]
        end

        subgraph Databases["<<execution environment>><br/>Database Layer"]
            MySQLAuth[("<<database>><br/>auth_db<br/>(MySQL 8.0)")]
            MySQLOrder[("<<database>><br/>order_db<br/>(MySQL 8.0)")]
            MySQLPayment[("<<database>><br/>payment_db<br/>(MySQL 8.0)")]
            MongoUser[("<<database>><br/>user_db<br/>(MongoDB 7.0)")]
            MongoReview[("<<database>><br/>review_db<br/>(MongoDB 7.0)")]
            MongoNotification[("<<database>><br/>notification_db<br/>(MongoDB 7.0)")]
        end
    end

    %% Client Connections
    ClientPC ---|HTTPS| FrontendUI
    FrontendUI ---|REST API| GatewayService

    %% Gateway to Services
    GatewayService -.->|deploy| AuthService
    GatewayService -.->|deploy| UserService
    GatewayService -.->|deploy| OrderService
    GatewayService -.->|deploy| PaymentService
    GatewayService -.->|deploy| ReviewService
    GatewayService -.->|deploy| NotificationService

    %% Services to Databases
    AuthService -->|SQL| MySQLAuth
    OrderService -->|SQL| MySQLOrder
    PaymentService -->|SQL| MySQLPayment
    UserService -->|NoSQL| MongoUser
    ReviewService -->|NoSQL| MongoReview
    NotificationService -->|NoSQL| MongoNotification

    %% Services to Infrastructure
    OrderService ==>|Publish Events| RabbitMQ
    PaymentService ==>|Publish Events| RabbitMQ
    ReviewService ==>|Publish Events| RabbitMQ
    RabbitMQ ==>|Subscribe| NotificationService

    GatewayService -.->|Cache| Redis
    AuthService -.->|Session| Redis

    %% Styling
    classDef client fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    classDef location fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef artifact fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef infrastructure fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px

    class ClientPC client
    class Internet,AWS location
    class FrontendUI,GatewayService,AuthService,UserService,OrderService,PaymentService,ReviewService,NotificationService artifact
    class MySQLAuth,MySQLOrder,MySQLPayment,MongoUser,MongoReview,MongoNotification database
    class RabbitMQ,Redis infrastructure
```

---

### 部署图说明

#### 📋 UML Stereotypes（构造型说明）

| Stereotype | 含义 | 示例 |
|-----------|------|------|
| `<<location>>` | 部署位置/网络区域 | Internet, AWS Cloud |
| `<<execution environment>>` | 执行环境 | Frontend Server, Microservices Cluster |
| `<<device>>` | 物理设备 | Client PC |
| `<<artifact>>` | 软件制品 | gateway-service.jar, user-service.jar |
| `<<database>>` | 数据库实例 | auth_db, order_db |
| `<<node>>` | 基础设施节点 | RabbitMQ, Redis |

---

#### 🏗️ 部署架构说明

##### **1. Internet层（<<location>>）**
- **Client PC**: 用户通过浏览器访问系统
- **Protocol**: HTTPS
- **Connection**: 访问部署在AWS的Frontend UI

##### **2. AWS Cloud层（<<location>>）**

###### **Frontend Server（<<execution environment>>）**
- **Artifact**: Frontend UI (Vue.js + Vite)
- **Port**: 80 (HTTP), 443 (HTTPS)
- **Purpose**: 提供Web界面（Customer, Provider, Admin）
- **Technology**: Vue.js 3, Vite打包

###### **API Gateway（<<execution environment>>）**
- **Artifact**: gateway-service.jar (FastAPI)
- **Port**: 8080
- **Components**: Router, JWT Handler, Rate Limiter, Middleware
- **Purpose**: 统一入口、认证、限流、路由转发

###### **Microservices Cluster（<<execution environment>>）**

6个独立部署的微服务：

| Service | Port | Database | Technology |
|---------|------|----------|------------|
| **auth-service** | 8000 | MySQL (auth_db) | FastAPI + SQLAlchemy |
| **user-service** | 8002 | MongoDB (user_db) | FastAPI + Motor |
| **order-service** | 8003 | MySQL (order_db) | FastAPI + SQLAlchemy |
| **payment-service** | 8004 | MySQL (payment_db) | FastAPI + SQLAlchemy |
| **review-service** | 8005 | MongoDB (review_db) | FastAPI + Motor |
| **notification-service** | 8006 | MongoDB (notification_db) | FastAPI + Motor |

###### **Infrastructure（基础设施）**

**RabbitMQ（<<node>>）**:
- **Purpose**: 消息队列，事件驱动通信
- **Ports**: 5672 (AMQP), 15672 (Management)
- **Exchanges**: order_events, payment_events, review_events
- **Consumers**: Notification Service

**Redis（<<node>>）**:
- **Purpose**: 缓存和会话管理
- **Port**: 6379
- **Usage**: Rate limiting, Session cache, Notification cache

###### **Database Layer（<<execution environment>>）**

**MySQL 8.0** (AWS RDS Multi-AZ):
- `auth_db`: 用户认证数据（users, roles表）
- `order_db`: 订单数据（orders表）
- `payment_db`: 支付数据（payments, refunds表）

**MongoDB 7.0** (MongoDB Atlas):
- `user_db`: 用户资料（customer_profiles, provider_profiles集合）
- `review_db`: 评价数据（reviews, ratings集合）
- `notification_db`: 通知消息（customer_inbox, provider_inbox集合）

---

#### 🔄 通信模式

| 连接类型 | 表示 | 说明 |
|---------|------|------|
| **实线箭头** `---` | 同步HTTP调用 | Client → Frontend, Services → Database |
| **虚线箭头** `-.->` | 部署关系/缓存访问 | Gateway deploy Services, Services → Redis |
| **粗箭头** `==>` | 异步消息通信 | Services → RabbitMQ → Notification |

---

#### 📊 部署特点

**架构风格**: Microservices  
**通信方式**: REST (同步) + Event-Driven (异步)  
**数据策略**: Polyglot Persistence (MySQL + MongoDB)  
**云平台**: AWS (RDS + EC2) + MongoDB Atlas  
**高可用**: MySQL Multi-AZ, MongoDB 3-node Replica Set  
**消息队列**: RabbitMQ Topic Exchange  
**缓存**: Redis (Rate Limiting + Session)

---

#### ✅ 关键设计决策

1. **API Gateway模式**: 统一入口，简化客户端调用
2. **Database per Service**: 每个服务独立数据库，避免耦合
3. **Event-Driven Architecture**: RabbitMQ解耦服务间通信
4. **Polyglot Persistence**: 
   - MySQL: 事务性数据（Auth, Order, Payment）
   - MongoDB: 灵活schema（User, Review, Notification）
5. **Stateless Services**: 服务无状态，便于水平扩展
6. **Centralized Cache**: Redis统一缓存，提升性能

---

## 简化版架构图（层次清晰）
POST /login           # 用户登录
POST /verify-token    # Token验证
POST /refresh-token   # Token刷新

# Models
User Model (user.py):
  - id: BIGINT PRIMARY KEY
  - username: VARCHAR(100) UNIQUE
  - email: VARCHAR(255) UNIQUE
  - password_hash: VARCHAR(255)
  - role_id: INT (FK to roles)

Role Model (role.py):
  - id: INT PRIMARY KEY
  - name: VARCHAR(50) # 'customer', 'provider', 'admin'
```

**Database Tables**:
- `users`: 用户账号信息
- `roles`: 角色定义

---

##### 5️⃣ **User Service Server (用户服务器)**

**Execution Environment**: Python 3.11 + Uvicorn  
**Artifact**: `user-service.jar` (FastAPI + Motor)  
**Port**: 8002  
**Database**: MongoDB 7.0 (`user_db`)  
**Code Location**: `services/user-service/src/user_service/`

**Components**:

```python
# API Endpoints
GET /customers/{id}/profile        # 获取客户资料
PUT /customers/{id}/profile        # 更新客户资料
GET /providers/{id}/profile        # 获取服务商资料
PUT /providers/{id}/profile        # 更新服务商资料

# Document Schemas
Customer Profile:
  - user_id: int
  - full_name: str
  - phone: str
  - address: {province, city, detail}
  - preferences: {location, service_types}

Provider Profile:
  - user_id: int
  - full_name: str
  - skills: [str]
  - certifications: [{name, file_url}]
  - service_areas: [str]
  - rating: float
  - verified: bool
```

**MongoDB Collections**:
- `customer_profiles`: 客户资料（灵活schema）
- `provider_profiles`: 服务商资料（嵌套文档）

---

##### 6️⃣ **Order Service Server (订单服务器)**

**Execution Environment**: Python 3.11 + Uvicorn  
**Artifact**: `order-service.jar` (FastAPI + SQLAlchemy)  
**Port**: 8003  
**Database**: MySQL 8.0 (`order_db`)  
**Code Location**: `services/order-service/src/order_service/`

**Components**:

```python
# API Endpoints
POST /customer/orders/publish           # 客户发布订单
PUT /provider/orders/{id}/accept       # 服务商接单
GET /orders/{id}                       # 获取订单详情
PUT /orders/{id}/status                # 更新订单状态

# Services
CustomerOrderService (customer_order_service.py):
  - publish_order()     # 创建订单 + 发布事件
  - cancel_order()      # 取消订单

ProviderOrderService (provider_order_service.py):
  - accept_order()      # 接受订单（乐观锁）
  - update_order_status()  # 更新状态

# Event Publisher
EventPublisher (event_publisher.py):
  - publish_order_created()
  - publish_order_accepted()
  - publish_order_status_changed()

# Model
Order Model (order.py):
  - id: BIGINT
  - service_type: ENUM
  - status: ENUM (pending_review, pending, accepted, ...)
  - location: ENUM (NORTH, SOUTH, EAST, WEST, MID)
  - payment_status: ENUM (unpaid, paid)
```

**Database Table**:
- `orders`: 订单核心数据（ACID事务保证）

---

##### 7️⃣ **Payment Service Server (支付服务器)**

**Execution Environment**: Python 3.11 + Uvicorn  
**Artifact**: `payment-service.jar` (FastAPI + SQLAlchemy)  
**Port**: 8004  
**Database**: MySQL 8.0 (`payment_db`)  
**Code Location**: `services/payment-service/src/payment_service/`

**Components**:

```python
# API Endpoints
POST /payments              # 创建支付
GET /payments/{id}          # 查询支付状态
POST /refunds              # 创建退款

# Service
PaymentService (payment_service.py):
  - process_payment()    # 调用第三方支付API
  - create_refund()      # 处理退款

# Models
Payment Model (payment.py):
  - id: BIGINT
  - order_id: BIGINT
  - transaction_id: VARCHAR(255) UNIQUE
  - amount: DECIMAL(10,2)
  - status: ENUM (pending, completed, failed)

Refund Model (refund.py):
  - id: BIGINT
  - payment_id: BIGINT
  - amount: DECIMAL(10,2)
  - status: ENUM (pending, completed, rejected)
```

**Database Tables**:
- `payments`: 支付记录
- `refunds`: 退款记录
- `transactions`: 交易流水（审计）

---

##### 8️⃣ **Review Service Server (评价服务器)**

**Execution Environment**: Python 3.11 + Uvicorn  
**Artifact**: `review-service.jar` (FastAPI + Motor)  
**Port**: 8005  
**Database**: MongoDB 7.0 (`review_db`)  
**Code Location**: `services/review-service/src/review_service/`

**Components**:

```python
# API Endpoints
POST /reviews                      # 提交评价
GET /providers/{id}/reviews        # 查询服务商评价
GET /reviews/{id}                  # 评价详情

# Service
ReviewService (review_service.py):
  - create_review()         # 创建评价
  - calculate_rating()      # 计算评分

# Documents
Review Document:
  - order_id: int
  - customer_id: int
  - provider_id: int
  - rating: int (1-5)
  - comment: str
  - dimensions: {professionalism, attitude, punctuality}
  - images: [str]

Rating Aggregator:
  - provider_id: int
  - average_rating: float
  - total_reviews: int
  - rating_distribution: {5: 120, 4: 30, ...}
```

**MongoDB Collections**:
- `reviews`: 评价详情
- `ratings`: 聚合统计

---

##### 9️⃣ **Notification Service Server (通知服务器)**

**Execution Environment**: Python 3.11 + Uvicorn  
**Artifact**: `notification-service.jar` (FastAPI + Motor)  
**Port**: 8006  
**Database**: MongoDB 7.0 (`notification_db`)  
**Code Location**: `services/notification-service/src/notification_service/`

**Components**:

```python
# API Endpoints
GET /notifications              # 获取通知列表
PUT /notifications/{id}/read    # 标记已读

# Event Consumer
EventConsumer (consumer.py):
  - Subscribe to RabbitMQ
  - Handle 15+ event types

# Event Handlers
OrderEventHandler (order_event_handler.py):
  - handle_order_created()      # 通知匹配Providers
  - handle_order_accepted()     # 通知Customer和Provider
  - handle_order_cancelled()    # 通知相关方

# Service
NotificationService (notification_service.py):
  - create_notification()
  - mark_as_read()
  - get_unread_count()
```

**MongoDB Collections**:
- `customer_inbox`: 客户通知收件箱
- `provider_inbox`: 服务商通知收件箱

---

##### 🔟 **Infrastructure Layer (基础设施层)**

###### **RabbitMQ Message Broker**

**Node**: RabbitMQ Server 3.12  
**Ports**: 5672 (AMQP), 15672 (Management UI)  
**Type**: Topic Exchange

**Exchanges**:
```python
order_events:
  - Type: topic
  - Routing Keys: order.created, order.accepted, order.cancelled

payment_events:
  - Type: topic
  - Routing Keys: payment.initiated, payment.completed, payment.failed

review_events:
  - Type: topic
  - Routing Keys: review.created, rating.updated
```

**Queues**:
```python
order_queue:
  - Bindings: order_events + order.*
  - Consumer: Notification Service

payment_queue:
  - Bindings: payment_events + payment.*
  - Consumer: Notification Service

review_queue:
  - Bindings: review_events + review.*
  - Consumer: Notification Service
```

**Features**:
- ✅ Message Persistence (`durable=True`)
- ✅ Publisher Confirms
- ✅ Dead Letter Exchange
- ✅ Message TTL (24 hours)

---

###### **Redis Cache Server**

**Node**: Redis 7.0  
**Port**: 6379  
**Persistence**: RDB + AOF

**Cache Keys**:
```python
rate_limit:{user_id}:
  - TTL: 60 seconds
  - Value: Request count
  - Used by: Rate Limiter

session:{token}:
  - TTL: 3600 seconds (1 hour)
  - Value: User session data
  - Used by: JWT Handler

notification:order:{order_id}:
  - TTL: 3600 seconds
  - Value: Notification message
  - Used by: Notification Service
```

**Features**:
- ✅ In-Memory Performance
- ✅ Automatic Expiration
- ✅ Redis Sentinel (HA)

---

##### 1️⃣1️⃣ **Database Layer (数据库层)**

###### **AWS RDS MySQL 8.0 Cluster**

**Deployment**: Multi-AZ (us-east-1)  
**Instances**:

| Database | Instance Type | Size | Tables |
|----------|--------------|------|--------|
| **auth_db** | db.t3.small | 20GB | users, roles |
| **order_db** | db.t3.medium | 50GB | orders |
| **payment_db** | db.t3.small | 30GB | payments, refunds, transactions |

**Features**:
- ✅ Automatic Backups (7-day retention)
- ✅ Multi-AZ Failover (< 2 min)
- ✅ Read Replicas (optional)
- ✅ Encryption at Rest (AES-256)
- ✅ Connection Pooling (SQLAlchemy)

---

###### **MongoDB Atlas 7.0 Cluster**

**Deployment**: Cloud (AWS us-east-1)  
**Clusters**:

| Database | Cluster Tier | Size | Collections |
|----------|-------------|------|-------------|
| **user_db** | M10 | 10GB | customer_profiles, provider_profiles |
| **review_db** | M10 | 10GB | reviews, ratings |
| **notification_db** | M5 | 2GB | customer_inbox, provider_inbox |

**Features**:
- ✅ Auto-Scaling (Storage + Compute)
- ✅ Point-in-Time Recovery
- ✅ Atlas Search (Full-Text)
- ✅ Global Clusters (optional)
- ✅ TTL Indexes (Notification cleanup)

---

#### 🔄 Communication Protocols

| Type | Protocol | Port | Use Case |
|------|----------|------|----------|
| **Client → Frontend** | HTTPS | 443 | Web Application |
| **Frontend → Gateway** | HTTPS/REST | 8080 | API Calls |
| **Gateway → Services** | HTTP/REST | 8000-8006 | Service Communication |
| **Service → MySQL** | MySQL Protocol | 3306 | Database Access |
| **Service → MongoDB** | MongoDB Wire Protocol | 27017 | Database Access |
| **Service → RabbitMQ** | AMQP 0.9.1 | 5672 | Event Publishing |
| **Service → Redis** | Redis Protocol | 6379 | Cache Access |

---

#### 🎯 Deployment Characteristics

| Characteristic | Value |
|---------------|-------|
| **Architecture Style** | Microservices |
| **Communication** | Synchronous (REST) + Asynchronous (Events) |
| **Data Strategy** | Polyglot Persistence |
| **Scalability** | Horizontal (Services) + Vertical (DB) |
| **Availability** | Multi-AZ (Database), Replicas (Services) |
| **Security** | JWT Authentication, HTTPS, Encryption at Rest |
| **Monitoring** | Prometheus + Grafana (optional) |
| **Logging** | Centralized (ELK Stack, optional) |

---

#### 📊 Resource Requirements

| Component | CPU | RAM | Disk | Instances |
|-----------|-----|-----|------|-----------|
| **Frontend** | 1 core | 1GB | 10GB | 1-2 |
| **API Gateway** | 2 cores | 2GB | 10GB | 2-3 |
| **Auth Service** | 1 core | 1GB | 10GB | 1-2 |
| **User Service** | 1 core | 1GB | 10GB | 1-2 |
| **Order Service** | 2 cores | 2GB | 10GB | 2-4 |
| **Payment Service** | 1 core | 1GB | 10GB | 1-2 |
| **Review Service** | 1 core | 1GB | 10GB | 1-2 |
| **Notification Service** | 1 core | 1GB | 10GB | 1-2 |
| **RabbitMQ** | 2 cores | 4GB | 20GB | 1-3 |
| **Redis** | 1 core | 2GB | 10GB | 1-3 |
| **MySQL (each)** | 2 cores | 4-8GB | 20-50GB | 1 (Multi-AZ) |
| **MongoDB (each)** | 2 cores | 2-10GB | 2-10GB | 3-node replica |

---

#### ✅ Deployment Validation Checklist

- [ ] All services can connect to their databases
- [ ] API Gateway can route to all 6 services
- [ ] RabbitMQ exchanges and queues are created
- [ ] Redis is accessible from Gateway and Notification Service
- [ ] JWT tokens can be validated across services
- [ ] Order creation triggers notification events
- [ ] Payment completion updates order status
- [ ] Frontend can authenticate and make API calls
- [ ] Rate limiting works correctly
- [ ] Database backups are configured
- [ ] SSL/TLS certificates are valid
- [ ] Monitoring and logging are operational

---

## 简化版架构图（层次清晰）

```mermaid
graph TB
    subgraph "Layer 1: Client"
        Client[Web Browsers]
    end

    subgraph "Layer 2: Security"
        Security[CDN + WAF + SSL]
    end

    subgraph "Layer 3: Frontend"
        Frontend[Vue.js SPAs<br/>Customer | Provider | Admin]
    end

    subgraph "Layer 4: API Gateway"
        Gateway[API Gateway<br/>Auth • Rate Limit • Routing]
        GatewayCache[(Redis)]
    end

    subgraph "Layer 5: Microservices"
        Services[6 Microservices<br/>Auth | User | Order<br/>Payment | Review | Notification]
    end

    subgraph "Layer 6: Infrastructure"
        MQ[Message Queue<br/>RabbitMQ]
        Cache[(Cache<br/>Redis)]
        DB[(Databases<br/>MySQL x3<br/>MongoDB x3)]
    end

    subgraph "Layer 7: Observability"
        Monitor[Monitoring<br/>Prometheus + Grafana + ELK]
    end

    Client --> Security
    Security --> Frontend
    Frontend --> Gateway
    Gateway --> GatewayCache
    Gateway --> Services
    Services --> MQ
    Services --> Cache
    Services --> DB
    Services --> Monitor

    classDef layer1 fill:#e3f2fd,stroke:#1565c0
    classDef layer2 fill:#fff9c4,stroke:#f57f17
    classDef layer3 fill:#e1f5fe,stroke:#0277bd
    classDef layer4 fill:#fff3e0,stroke:#e65100
    classDef layer5 fill:#c8e6c9,stroke:#2e7d32
    classDef layer6 fill:#ffccbc,stroke:#bf360c
    classDef layer7 fill:#f3e5f5,stroke:#4a148c

    class Client layer1
    class Security layer2
    class Frontend layer3
    class Gateway,GatewayCache layer4
    class Services layer5
    class MQ,Cache,DB layer6
    class Monitor layer7
```

---

## 服务通信模式图

```mermaid
graph LR
    subgraph "Synchronous Communication"
        User[User Service] -->|HTTP| Auth[Auth Service]
        Order[Order Service] -->|HTTP| User
        Payment[Payment Service] -->|HTTP| Order
    end

    subgraph "Asynchronous Communication"
        OrderSvc[Order Service] ==>|Publish| MQ[RabbitMQ]
        PaymentSvc[Payment Service] ==>|Publish| MQ
        ReviewSvc[Review Service] ==>|Publish| MQ
        MQ ==>|Subscribe| Notify[Notification Service]
    end

    classDef sync fill:#c8e6c9,stroke:#2e7d32
    classDef async fill:#bbdefb,stroke:#1565c0
    classDef mq fill:#ffccbc,stroke:#bf360c

    class User,Auth,Order,Payment sync
    class OrderSvc,PaymentSvc,ReviewSvc,Notify async
    class MQ mq
```

---

## 数据流图（以订单创建为例）

```mermaid
sequenceDiagram
    participant C as Customer Web
    participant G as API Gateway
    participant A as Auth Service
    participant O as Order Service
    participant U as User Service
    participant MQ as RabbitMQ
    participant N as Notification Service
    participant DB as Order DB

    C->>G: POST /orders (with JWT)
    G->>A: Verify JWT Token
    A-->>G: Token Valid
    G->>O: Create Order Request
    O->>U: Get User Profile
    U-->>O: User Data
    O->>DB: Save Order
    DB-->>O: Order Saved
    O->>MQ: Publish order_created Event
    MQ->>N: Consume Event
    N->>N: Send Notification
    O-->>G: Order Created Response
    G-->>C: 201 Created
```

---

## 部署架构图（Kubernetes）

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress Layer"
            Ingress[Nginx Ingress<br/>Load Balancer]
        end

        subgraph "Service Mesh"
            Istio[Istio Service Mesh<br/>Optional]
        end

        subgraph "Application Pods"
            AuthPod[Auth Pod x3]
            UserPod[User Pod x3]
            OrderPod[Order Pod x3]
            PaymentPod[Payment Pod x2]
            ReviewPod[Review Pod x2]
            NotifyPod[Notification Pod x2]
        end

        subgraph "StatefulSets"
            MySQL[MySQL StatefulSet]
            Mongo[MongoDB StatefulSet]
            RabbitPod[RabbitMQ Pod]
            RedisPod[Redis Pod]
        end

        subgraph "Monitoring Stack"
            PromPod[Prometheus]
            GrafanaPod[Grafana]
        end
    end

    Internet[Internet] --> Ingress
    Ingress --> Istio
    Istio --> AuthPod
    Istio --> UserPod
    Istio --> OrderPod
    Istio --> PaymentPod
    Istio --> ReviewPod
    Istio --> NotifyPod

    AuthPod --> MySQL
    OrderPod --> MySQL
    PaymentPod --> MySQL
    UserPod --> Mongo
    ReviewPod --> Mongo
    NotifyPod --> Mongo

    OrderPod --> RabbitPod
    PaymentPod --> RabbitPod
    ReviewPod --> RabbitPod
    NotifyPod --> RabbitPod

    AuthPod --> RedisPod
    UserPod --> RedisPod

    AuthPod -.-> PromPod
    UserPod -.-> PromPod
    OrderPod -.-> PromPod
    PromPod --> GrafanaPod
```

---

## 如何使用这些图

### 1. GitHub README
将 Mermaid 代码直接粘贴到 `README.md`：
\`\`\`mermaid
graph TB
    ...
\`\`\`

### 2. 在线工具
- [Mermaid Live Editor](https://mermaid.live/)
- 粘贴代码，导出 PNG/SVG

### 3. VS Code
安装插件：
- Markdown Preview Mermaid Support
- Mermaid Editor

### 4. 文档工具
- GitBook
- Docusaurus
- MkDocs (with mermaid plugin)

---

## 图例说明

```
━━━━━  实线箭头：HTTP 同步调用
━ ━ ━  虚线箭头：缓存/监控等辅助连接
══════  粗箭头：消息队列异步通信
```

**颜色编码**:
- 🔵 蓝色：前端层
- 🟡 黄色：网关层
- 🟢 绿色：服务层
- 🟠 橙色：数据层
- 🟣 紫色：基础设施层
- 🔴 红色：监控层

---

## DDD 领域驱动设计图

### 服务组件与领域职责

```mermaid
graph TB
    subgraph API["API Gateway Service"]
        APIGateway["API Gateway<br/>_________________<br/><br/>Route requests,<br/>authenticate users,<br/>rate limiting"]
    end

    subgraph Auth["Auth Service"]
        AuthService["Auth Service<br/>_________________<br/><br/>User registration,<br/>login/logout,<br/>JWT token management,<br/>OAuth integration"]
    end

    subgraph User["User Service"]
        UserService["User Service<br/>_________________<br/><br/>Manage user profiles,<br/>roles (customer/provider),<br/>skills & portfolios,<br/>user verification"]
    end

    subgraph Order["Order Service"]
        OrderService["Order Service<br/>_________________<br/><br/>Create orders,<br/>track order status,<br/>manage order lifecycle,<br/>order history"]
    end

    subgraph Payment["Payment Service"]
        PaymentService["Payment Service<br/>_________________<br/><br/>Process payments,<br/>manage transactions,<br/>payment methods,<br/>refunds"]
    end

    subgraph Review["Review Service"]
        ReviewService["Review Service<br/>_________________<br/><br/>Submit reviews,<br/>rating system,<br/>review moderation,<br/>provider reputation"]
    end

    subgraph Notification["Notification Service"]
        NotificationService["Notification Service<br/>_________________<br/><br/>Send notifications,<br/>email/SMS/push alerts,<br/>event-driven messaging"]
    end

    %% API Gateway connections
    APIGateway -->|Verify token| AuthService
    APIGateway -->|Route requests| UserService
    APIGateway -->|Route requests| OrderService
    APIGateway -->|Route requests| PaymentService
    APIGateway -->|Route requests| ReviewService

    %% Service interactions
    OrderService -->|Verify user| UserService
    OrderService -.->|Order created event| NotificationService
    
    PaymentService -->|Get order details| OrderService
    PaymentService -.->|Payment completed event| NotificationService
    
    ReviewService -->|Verify order| OrderService
    ReviewService -.->|Review submitted event| NotificationService

    %% Styling
    classDef gateway fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef service fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    classDef messaging fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class APIGateway gateway
    class AuthService,UserService,OrderService,PaymentService,ReviewService service
    class NotificationService messaging
```

---

## DDD 图解说明

### 🎯 什么是 DDD（领域驱动设计）？

**Domain-Driven Design** 强调以业务领域为核心，将复杂系统划分为多个**限界上下文（Bounded Context）**，每个上下文负责一个独立的业务领域。

---

### 📊 图中的核心元素

#### 1️⃣ **服务边界（Bounded Context）**

每个服务框代表一个独立的业务领域：

| 服务 | 领域职责 | 核心能力 |
|------|---------|---------|
| **API Gateway** | 统一入口 | 路由、认证、限流 |
| **Auth Service** | 身份认证 | 注册、登录、JWT、OAuth |
| **User Service** | 用户管理 | 资料、角色、技能、认证 |
| **Order Service** | 订单管理 | 创建订单、状态追踪、历史记录 |
| **Payment Service** | 支付处理 | 支付、交易、退款 |
| **Review Service** | 评价系统 | 提交评价、评分、信誉 |
| **Notification Service** | 消息通知 | 邮件、短信、推送 |

#### 2️⃣ **服务交互模式**

**同步调用（实线箭头）**：
- API Gateway → Auth/User/Order/Payment/Review
- Order Service → User Service（验证用户）
- Payment Service → Order Service（获取订单详情）
- Review Service → Order Service（验证订单）

**异步事件（虚线箭头）**：
- Order Service ──> Notification（订单创建事件）
- Payment Service ──> Notification（支付完成事件）
- Review Service ──> Notification（评价提交事件）

#### 3️⃣ **通信协议**

```
━━━━━  实线：同步 HTTP/REST 调用（请求-响应）
- - - -  虚线：异步消息事件（通过 RabbitMQ）
```

---

### 🔄 典型业务流程示例

#### 📦 订单创建流程

```
1. Customer → API Gateway（创建订单请求）
2. API Gateway → Auth Service（验证 JWT）
3. API Gateway → Order Service（转发请求）
4. Order Service → User Service（验证用户信息）
5. Order Service → Database（保存订单）
6. Order Service → RabbitMQ（发布 order_created 事件）
7. Notification Service ← RabbitMQ（消费事件，发送通知）
```

#### � 支付流程

```
1. Customer → API Gateway（支付请求）
2. API Gateway → Payment Service
3. Payment Service → Order Service（获取订单详情）
4. Payment Service → Database（保存交易记录）
5. Payment Service → RabbitMQ（发布 payment_completed 事件）
6. Notification Service（发送支付成功通知）
```

---

### 🏗️ DDD 分层架构（单个服务内部）

```
┌─────────────────────────────────┐
│   API Layer (FastAPI)           │  路由、请求验证
├─────────────────────────────────┤
│   Application Layer             │  用例编排、事件处理
├─────────────────────────────────┤
│   Domain Layer ⭐                │  业务逻辑、领域模型
│   - Entities (实体)             │  - User, Order, Payment
│   - Value Objects (值对象)      │  - Money, Status
│   - Domain Services (领域服务)  │  - OrderLifecycle
├─────────────────────────────────┤
│   Infrastructure Layer          │  数据库、消息队列
└─────────────────────────────────┘
```

---

### ✅ DDD 核心原则在项目中的体现

| DDD 概念 | 项目实现 |
|----------|---------|
| **Bounded Context** | 7 个独立微服务（包括 Gateway） |
| **Domain Events** | RabbitMQ 消息队列（order_events, payment_events, review_events） |
| **Aggregate Root** | User, Order, Payment, Review 等核心实体 |
| **Repository Pattern** | SQLAlchemy/Motor 数据访问层 |
| **Anti-Corruption Layer** | API Gateway 作为防腐层 |
| **Event-Driven Architecture** | 异步事件解耦服务依赖 |

---

### 🎯 DDD 的核心价值

1. **清晰的业务边界** - 每个服务对应一个业务领域
2. **高内聚低耦合** - 服务内部高内聚，服务间通过事件松耦合
3. **独立演进** - 每个服务可独立开发、部署、扩展
4. **易于理解** - 技术架构与业务结构对齐
5. **故障隔离** - 单个服务故障不影响整体系统

---

## 事件驱动架构图（Event-Driven Architecture）

### Producer-Consumer 交互模式

```mermaid
graph TB
    subgraph Producers["Event Producers"]
        OrderProducer["Order Service<br/>_________________<br/><br/>Publishes:<br/>• order.created<br/>• order.accepted<br/>• order.cancelled<br/>• order.status_changed<br/>• order.approved<br/>• order.rejected"]
        
        PaymentProducer["Payment Service<br/>_________________<br/><br/>Publishes:<br/>• payment.initiated<br/>• payment.completed<br/>• payment.failed<br/>• refund.processed"]
        
        ReviewProducer["Review Service<br/>_________________<br/><br/>Publishes:<br/>• review.created<br/>• rating.updated"]
        
        AuthProducer["Auth Service<br/>_________________<br/><br/>Publishes:<br/>• user.registered"]
        
        UserProducer["User Service<br/>_________________<br/><br/>Publishes:<br/>• profile.created<br/>• profile.updated"]
    end

    subgraph EventBus["Event Bus (RabbitMQ)"]
        OrderExchange["📮 order_events<br/>Exchange<br/>(Topic)"]
        PaymentExchange["📮 payment_events<br/>Exchange<br/>(Topic)"]
        ReviewExchange["📮 review_events<br/>Exchange<br/>(Topic)"]
        AuthExchange["📮 auth_events<br/>Exchange<br/>(Topic)"]
        UserExchange["📮 user_events<br/>Exchange<br/>(Topic)"]
    end

    subgraph Queues["Message Queues"]
        OrderQueue["📥 order_queue<br/>Bindings:<br/>• order.*"]
        PaymentQueue["📥 payment_queue<br/>Bindings:<br/>• payment.*"]
        ReviewQueue["📥 review_queue<br/>Bindings:<br/>• review.*"]
    end

    subgraph Consumer["Event Consumer"]
        NotificationConsumer["Notification Service<br/>_________________<br/><br/>Subscribes to:<br/>• order.created<br/>• order.accepted<br/>• order.cancelled<br/>• order.status_changed<br/>• order.approved<br/>• order.rejected<br/>• payment.completed<br/>• payment.failed<br/>• review.created"]
    end

    %% Producer to Exchange
    OrderProducer -->|Publish| OrderExchange
    PaymentProducer -->|Publish| PaymentExchange
    ReviewProducer -->|Publish| ReviewExchange
    AuthProducer -->|Publish| AuthExchange
    UserProducer -->|Publish| UserExchange

    %% Exchange to Queue
    OrderExchange -->|Route| OrderQueue
    PaymentExchange -->|Route| PaymentQueue
    ReviewExchange -->|Route| ReviewQueue

    %% Queue to Consumer
    OrderQueue -->|Subscribe| NotificationConsumer
    PaymentQueue -->|Subscribe| NotificationConsumer
    ReviewQueue -->|Subscribe| NotificationConsumer

    %% Styling
    classDef producer fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef exchange fill:#fff9c4,stroke:#f57c00,stroke-width:2px
    classDef queue fill:#e1bee7,stroke:#7b1fa2,stroke-width:2px
    classDef consumer fill:#bbdefb,stroke:#1565c0,stroke-width:2px

    class OrderProducer,PaymentProducer,ReviewProducer,AuthProducer,UserProducer producer
    class OrderExchange,PaymentExchange,ReviewExchange,AuthExchange,UserExchange exchange
    class OrderQueue,PaymentQueue,ReviewQueue queue
    class NotificationConsumer consumer
```

---

## 事件流详细说明

### 📊 Exchange (交换机) 配置

| Exchange Name | Type | Description |
|--------------|------|-------------|
| **order_events** | Topic | 订单相关事件总线 |
| **payment_events** | Topic | 支付相关事件总线 |
| **review_events** | Topic | 评价相关事件总线 |
| **auth_events** | Topic | 认证相关事件总线 |
| **user_events** | Topic | 用户资料相关事件总线 |

### 📮 事件列表（按服务分类）

#### 1️⃣ Order Service (生产者)

```python
# Exchange: order_events
- order.created          # 订单创建
- order.accepted         # 服务商接受订单
- order.cancelled        # 订单取消
- order.status_changed   # 订单状态变更
- order.approved         # 订单审核通过
- order.rejected         # 订单被拒绝
```

#### 2️⃣ Payment Service (生产者)

```python
# Exchange: payment_events
- payment.initiated      # 支付发起
- payment.completed      # 支付完成
- payment.failed         # 支付失败
- refund.processed       # 退款处理完成
```

#### 3️⃣ Review Service (生产者)

```python
# Exchange: review_events
- review.created         # 评价创建
- rating.updated         # 评分更新
```

#### 4️⃣ Auth Service (生产者)

```python
# Exchange: auth_events
- user.registered        # 用户注册
```

#### 5️⃣ User Service (生产者)

```python
# Exchange: user_events
- profile.created        # 用户资料创建
- profile.updated        # 用户资料更新
```

#### 6️⃣ Notification Service (消费者)

订阅所有事件并发送通知：
- ✉️ Email 通知
- 📱 SMS 短信
- 🔔 Push 推送
- 💬 站内消息

---

### 🔄 典型事件流程示例

#### 场景 1: 订单创建流程

```
1. Customer → Order Service: 创建订单 (HTTP)
2. Order Service → order_events: 发布 order.created 事件
3. order_events → order_queue: 路由消息
4. order_queue → Notification Service: 推送消息
5. Notification Service: 发送邮件/短信给 customer 和 provider
```

#### 场景 2: 支付完成流程

```
1. Customer → Payment Service: 完成支付 (HTTP)
2. Payment Service → payment_events: 发布 payment.completed 事件
3. payment_events → payment_queue: 路由消息
4. payment_queue → Notification Service: 推送消息
5. Notification Service: 发送支付成功通知
```

#### 场景 3: 评价提交流程

```
1. Customer → Review Service: 提交评价 (HTTP)
2. Review Service → review_events: 发布 review.created 事件
3. review_events → review_queue: 路由消息
4. review_queue → Notification Service: 推送消息
5. Notification Service: 通知 provider 收到新评价
```

---

### 🏗️ RabbitMQ 架构特点

#### 1️⃣ **Exchange 类型: Topic**

```
Topic Exchange 支持灵活的路由模式：
- order.*          匹配所有 order 事件
- payment.completed 只匹配支付完成事件
- *.created        匹配所有创建事件
```

#### 2️⃣ **Queue 绑定策略**

```python
# Notification Service 队列绑定
order_queue:
  - Binding: order_events + order.*
  
payment_queue:
  - Binding: payment_events + payment.*
  
review_queue:
  - Binding: review_events + review.*
```

#### 3️⃣ **消息持久化**

```python
# 所有消息都持久化，防止 RabbitMQ 重启丢失
Message(
    body=event_data,
    delivery_mode=2,  # Persistent
    content_type="application/json"
)
```

---

### ✅ 事件驱动架构的优势

| 优势 | 说明 |
|------|------|
| **异步解耦** | 服务间无需同步等待，提升性能 |
| **可扩展性** | 新增消费者无需修改生产者 |
| **故障容错** | 消息队列缓冲，消费者暂时宕机不丢消息 |
| **事件溯源** | 所有事件可追溯和重放 |
| **弹性伸缩** | 消费者可水平扩展处理高并发 |

---

### 🎯 实际代码示例

#### 生产者 (Order Service)

```python
# order_service/services/customer_order_service.py
async def create_order(data: CreateOrderDTO):
    order = await order_repo.create(data)
    
    # 发布事件
    event = OrderCreatedEvent(
        order_id=order.id,
        customer_id=order.customer_id,
        provider_id=order.provider_id,
        total_amount=order.total_amount
    )
    await EventPublisher.publish_order_created(event)
    
    return order
```

#### 消费者 (Notification Service)

```python
# notification_service/events/handlers/order_event_handler.py
async def handle_order_created(message: AbstractIncomingMessage):
    async with message.process():
        event_data = json.loads(message.body.decode())
        
        # 发送通知给客户
        await send_email(
            to=customer_email,
            subject="订单创建成功",
            body=f"订单 #{event_data['order_id']} 已创建"
        )
        
        # 发送通知给服务商
        await send_email(
            to=provider_email,
            subject="新订单通知",
            body="您有一个新订单等待处理"
        )
```

---

## 多语言持久化设计图（Polyglot Persistence）

### 数据库架构与服务映射

```mermaid
graph TB
    subgraph Services["Microservices Layer"]
        Auth["Auth Service<br/>(FastAPI + SQLAlchemy)"]
        User["User Service<br/>(FastAPI + Motor)"]
        Order["Order Service<br/>(FastAPI + SQLAlchemy)"]
        Payment["Payment Service<br/>(FastAPI + SQLAlchemy)"]
        Review["Review Service<br/>(FastAPI + Motor)"]
        Notification["Notification Service<br/>(FastAPI + Motor)"]
    end

    subgraph MySQL["AWS RDS MySQL Instances"]
        AuthDB[("🗄️ Auth Database<br/>(MySQL 8.0)<br/>_________________<br/><br/>Tables:<br/>• users<br/>• roles")]
        
        OrderDB[("🗄️ Order Database<br/>(MySQL 8.0)<br/>_________________<br/><br/>Tables:<br/>• orders")]
        
        PaymentDB[("🗄️ Payment Database<br/>(MySQL 8.0)<br/>_________________<br/><br/>Tables:<br/>• payments<br/>• transactions")]
    end

    subgraph MongoDB["MongoDB Atlas Clusters"]
        UserDB[("🍃 User Database<br/>(MongoDB 7.0)<br/>_________________<br/><br/>Collections:<br/>• customer_profiles")]
        
        ReviewDB[("🍃 Review Database<br/>(MongoDB 7.0)<br/>_________________<br/><br/>Collections:<br/>• reviews<br/>• ratings")]
        
        NotificationDB[("🍃 Notification Database<br/>(MongoDB 7.0)<br/>_________________<br/><br/>Collections:<br/>• customer_inbox<br/>• provider_inbox")]
    end

    %% Service to Database connections
    Auth -->|SQLAlchemy ORM| AuthDB
    Order -->|SQLAlchemy ORM| OrderDB
    Payment -->|SQLAlchemy ORM| PaymentDB
    User -->|Motor Driver| UserDB
    Review -->|Motor Driver| ReviewDB
    Notification -->|Motor Driver| NotificationDB

    %% Styling
    classDef service fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef mysql fill:#fff3e0,stroke:#e65100,stroke-width:3px
    classDef mongo fill:#c8e6c9,stroke:#1b5e20,stroke-width:3px

    class Auth,User,Order,Payment,Review,Notification service
    class AuthDB,OrderDB,PaymentDB mysql
    class UserDB,ReviewDB,NotificationDB mongo
```

---

## 数据库详细设计

### 🗄️ MySQL 数据库（AWS RDS）

#### 1️⃣ Auth Database (auth_db)

**服务**: Auth Service  
**ORM**: SQLAlchemy (Async)  
**连接**: `mysql+aiomysql://user:pass@auth-db.us-east-1.rds.amazonaws.com:3306/auth_db`

**表结构**:

```sql
-- users 表
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- roles 表
CREATE TABLE roles (
    id INT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255)
);
```

**数据特点**:
- ✅ 强一致性要求（用户认证）
- ✅ ACID 事务支持
- ✅ 用户关系型数据

---

#### 2️⃣ Order Database (order_db)

**服务**: Order Service  
**ORM**: SQLAlchemy (Async)  
**连接**: `mysql+aiomysql://user:pass@order-db.us-east-1.rds.amazonaws.com:3306/order_db`

**表结构**:

```sql
-- orders 表
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    provider_id BIGINT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    service_type ENUM('cleaning_repair', 'it_technology', 'education_training', 'life_health', 'design_consulting', 'other') NOT NULL,
    status ENUM('pending_review', 'pending', 'accepted', 'in_progress', 'completed', 'reviewed', 'cancelled') DEFAULT 'pending_review',
    price DECIMAL(10, 2) NOT NULL,
    location ENUM('NORTH', 'SOUTH', 'EAST', 'WEST', 'MID') NOT NULL,
    address VARCHAR(255),
    service_start_time DATETIME,
    service_end_time DATETIME,
    payment_status ENUM('unpaid', 'paid') DEFAULT 'unpaid',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_provider_id (provider_id),
    INDEX idx_status (status),
    INDEX idx_service_type (service_type)
);
```

**数据特点**:
- ✅ 订单状态流转需要事务
- ✅ 复杂查询（状态、时间范围）
- ✅ 金额精确计算（DECIMAL）

---

#### 3️⃣ Payment Database (payment_db)

**服务**: Payment Service  
**ORM**: SQLAlchemy (Async)  
**连接**: `mysql+aiomysql://user:pass@payment-db.us-east-1.rds.amazonaws.com:3306/payment_db`

**表结构**:

```sql
-- payments 表
CREATE TABLE payments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    provider_id BIGINT,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('simulated') DEFAULT 'simulated',
    status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    transaction_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_customer_id (customer_id),
    INDEX idx_status (status)
);

-- refunds 表
CREATE TABLE refunds (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    payment_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'completed', 'rejected') DEFAULT 'pending',
    reason TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    INDEX idx_payment_id (payment_id),
    INDEX idx_order_id (order_id)
);
```

**数据特点**:
- ✅ 金融交易数据（强一致性）
- ✅ 退款需要关联查询
- ✅ 审计日志需求

---

### 🍃 MongoDB 数据库（MongoDB Atlas）

#### 4️⃣ User Database (user_db)

**服务**: User Service  
**Driver**: Motor (Async)  
**连接**: `mongodb+srv://user:pass@user-cluster.xxxxx.mongodb.net/user_db`

**集合结构**:

```javascript
// customer_profiles 集合
{
  _id: ObjectId("..."),
  user_id: 123,
  full_name: "John Doe",
  phone_number: "+1234567890",
  address: "123 Main St",
  date_of_birth: ISODate("1990-01-01"),
  profile_picture_url: "https://...",
  bio: "Customer bio",
  preferences: {
    language: "en",
    currency: "USD"
  },
  created_at: ISODate("2025-10-01"),
  updated_at: ISODate("2025-10-24")
}

// provider_profiles 集合
{
  _id: ObjectId("..."),
  user_id: 456,
  full_name: "Jane Smith",
  phone_number: "+9876543210",
  service_categories: ["cleaning", "repair"],
  hourly_rate: 50.00,
  experience_years: 5,
  bio: "Professional cleaner",
  availability: {
    monday: ["09:00-17:00"],
    tuesday: ["09:00-17:00"]
  },
  verified: true,
  rating: 4.8,
  total_completed_orders: 156,
  created_at: ISODate("2025-01-01"),
  updated_at: ISODate("2025-10-24")
}
```

**数据特点**:
- ✅ 灵活的文档结构（用户资料可扩展）
- ✅ 嵌套数据（skills, portfolios）
- ✅ 快速读取性能

---

#### 5️⃣ Review Database (review_db)

**服务**: Review Service  
**Driver**: Motor (Async)  
**连接**: `mongodb+srv://user:pass@review-cluster.xxxxx.mongodb.net/review_db`

**集合结构**:

```javascript
// reviews 集合
{
  _id: ObjectId("..."),
  order_id: 789,
  customer_id: 123,
  provider_id: 456,
  stars: 5,
  content: "Excellent service!",
  images: ["review_img1.jpg", "review_img2.jpg"],
  helpful_count: 15,
  created_at: ISODate("2025-10-20")
}

// ratings 聚合集合
{
  _id: ObjectId("..."),
  provider_id: 456,
  average_rating: 4.8,
  total_reviews: 156,
  rating_distribution: {
    "5_stars": 120,
    "4_stars": 30,
    "3_stars": 5,
    "2_stars": 1,
    "1_star": 0
  },
  last_updated: ISODate("2025-10-24")
}
```

**数据特点**:
- ✅ 非结构化文本内容
- ✅ 评分统计聚合
- ✅ 快速全文搜索

---

#### 6️⃣ Notification Database (notification_db)

**服务**: Notification Service  
**Driver**: Motor (Async)  
**连接**: `mongodb+srv://user:pass@notification-cluster.xxxxx.mongodb.net/notification_db`

**集合结构**:

```javascript
// customer_inbox 集合
{
  _id: ObjectId("..."),
  customer_id: 123,
  order_id: 789,
  message: "Your order has been confirmed",
  is_read: false,
  created_at: ISODate("2025-10-24T10:30:00Z")
}

// provider_inbox 集合
{
  _id: ObjectId("..."),
  provider_id: 456,
  order_id: 789,
  message: "New order request received",
  is_read: false,
  created_at: ISODate("2025-10-24T10:30:00Z")
}
```

**数据特点**:
- ✅ 高写入频率
- ✅ 简单查询（按用户 ID）
- ✅ TTL 索引（自动删除旧通知）

---

## 数据库选型理由

### 📊 为什么选择 MySQL？

| 服务 | 理由 |
|------|------|
| **Auth Service** | 强一致性、用户认证不能出错、ACID 事务 |
| **Order Service** | 订单状态流转需要事务、复杂查询、JOIN 操作 |
| **Payment Service** | 金融交易、强一致性、审计需求 |

**MySQL 优势**:
- ✅ ACID 事务保证
- ✅ 外键约束
- ✅ 成熟的备份恢复方案
- ✅ 复杂查询优化

---

### 🍃 为什么选择 MongoDB？

| 服务 | 理由 |
|------|------|
| **User Service** | 用户资料灵活扩展、嵌套文档（skills, portfolios） |
| **Review Service** | 非结构化评论内容、全文搜索、快速读取 |
| **Notification Service** | 高写入频率、简单查询、TTL 自动清理 |

**MongoDB 优势**:
- ✅ 灵活的 Schema
- ✅ 高并发写入
- ✅ 水平扩展（Sharding）
- ✅ 文档型数据天然适配

---

## AWS 部署架构

### 🌐 MySQL 部署（AWS RDS）

```
┌─────────────────────────────────────┐
│  AWS Region: us-east-1              │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐   │
│  │  RDS MySQL Multi-AZ         │   │
│  ├─────────────────────────────┤   │
│  │  • auth_db (db.t3.small)    │   │
│  │  • order_db (db.t3.medium)  │   │
│  │  • payment_db (db.t3.small) │   │
│  └─────────────────────────────┘   │
│                                     │
│  Features:                          │
│  • Automatic backups (7 days)       │
│  • Multi-AZ failover                │
│  • Read replicas (optional)         │
│  • Encryption at rest               │
└─────────────────────────────────────┘
```

**连接配置**:
```python
# Auth Service
DATABASE_URL = "mysql+aiomysql://admin:password@auth-db.xxxxx.us-east-1.rds.amazonaws.com:3306/auth_db"

# Order Service
DATABASE_URL = "mysql+aiomysql://admin:password@order-db.xxxxx.us-east-1.rds.amazonaws.com:3306/order_db"

# Payment Service
DATABASE_URL = "mysql+aiomysql://admin:password@payment-db.xxxxx.us-east-1.rds.amazonaws.com:3306/payment_db"
```

---

### 🌐 MongoDB 部署（MongoDB Atlas）

```
┌─────────────────────────────────────┐
│  MongoDB Atlas (AWS us-east-1)      │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐   │
│  │  Cluster: user-cluster       │   │
│  │  Tier: M10 (2GB RAM)         │   │
│  │  Database: user_db           │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Cluster: review-cluster     │   │
│  │  Tier: M10 (2GB RAM)         │   │
│  │  Database: review_db         │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  Cluster: notification-cluster│  │
│  │  Tier: M5 (0.5GB RAM)        │   │
│  │  Database: notification_db   │   │
│  └─────────────────────────────┘   │
│                                     │
│  Features:                          │
│  • Auto-scaling                     │
│  • Point-in-time recovery           │
│  • Global clusters (optional)       │
│  • Atlas Search (full-text)         │
└─────────────────────────────────────┘
```

**连接配置**:
```python
# User Service
MONGODB_URL = "mongodb+srv://admin:password@user-cluster.xxxxx.mongodb.net/user_db?retryWrites=true&w=majority"

# Review Service
MONGODB_URL = "mongodb+srv://admin:password@review-cluster.xxxxx.mongodb.net/review_db?retryWrites=true&w=majority"

# Notification Service
MONGODB_URL = "mongodb+srv://admin:password@notification-cluster.xxxxx.mongodb.net/notification_db?retryWrites=true&w=majority"
```

---

## 连接池配置

### MySQL (SQLAlchemy)

```python
# services/auth-service/src/auth_service/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
    pool_pre_ping=True,      # 连接池健康检查
    pool_size=10,             # 连接池大小
    max_overflow=20,          # 最大溢出连接数
    pool_recycle=3600         # 连接回收时间（1小时）
)
```

### MongoDB (Motor)

```python
# services/user-service/src/user_service/core/mongodb.py
client = AsyncIOMotorClient(
    settings.MONGODB_URL,
    maxPoolSize=50,           # 最大连接数
    minPoolSize=10,           # 最小连接数
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=20000
)
```

---

## 数据迁移策略

### Alembic (MySQL)

```bash
# Auth Service
cd services/auth-service
alembic revision --autogenerate -m "create users and roles tables"
alembic upgrade head

# Order Service
cd services/order-service
alembic revision --autogenerate -m "create orders table"
alembic upgrade head

# Payment Service
cd services/payment-service
alembic revision --autogenerate -m "create payments and refunds tables"
alembic upgrade head
```

### MongoDB Schema Validation

```javascript
// User Service - customer_profiles 验证规则
db.createCollection("customer_profiles", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "full_name", "phone_number"],
      properties: {
        user_id: { bsonType: "int" },
        full_name: { bsonType: "string" },
        phone_number: { bsonType: "string" }
      }
    }
  }
});

// 创建索引
db.customer_profiles.createIndex({ user_id: 1 }, { unique: true });
db.provider_profiles.createIndex({ user_id: 1 }, { unique: true });
db.reviews.createIndex({ order_id: 1 });
db.customer_inbox.createIndex({ customer_id: 1, created_at: -1 });
```

---

## 性能优化建议

### 📈 MySQL 优化

1. **索引优化**
```sql
-- 复合索引
CREATE INDEX idx_order_customer_status ON orders(customer_id, status);
CREATE INDEX idx_payment_order_status ON payments(order_id, status);
```

2. **查询优化**
```sql
-- 使用 EXPLAIN 分析查询
EXPLAIN SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending';
```

3. **读写分离**
```python
# 主库（写操作）
PRIMARY_DB_URL = "mysql+aiomysql://admin:pass@primary.rds.amazonaws.com/order_db"

# 只读副本（读操作）
REPLICA_DB_URL = "mysql+aiomysql://admin:pass@replica.rds.amazonaws.com/order_db"
```

---

### 📈 MongoDB 优化

1. **索引策略**
```javascript
// 复合索引
db.customer_inbox.createIndex({ customer_id: 1, is_read: 1 });
db.reviews.createIndex({ provider_id: 1, created_at: -1 });
```

2. **TTL 索引（自动清理）**
```javascript
// 30天后自动删除已读通知
db.customer_inbox.createIndex(
  { created_at: 1 },
  { expireAfterSeconds: 2592000, partialFilterExpression: { is_read: true } }
);
```

3. **聚合管道优化**
```javascript
// 计算服务商平均评分
db.reviews.aggregate([
  { $match: { provider_id: 456 } },
  { $group: {
      _id: "$provider_id",
      avg_rating: { $avg: "$stars" },
      total_reviews: { $sum: 1 }
    }
  }
]);
```

---

## 💡 Polyglot Persistence 核心优势

| 优势 | 说明 |
|------|------|
| **技术选型灵活** | 根据数据特性选择最合适的数据库 |
| **性能优化** | MySQL 处理事务，MongoDB 处理高并发写入 |
| **成本优化** | 不同负载使用不同规格的数据库实例 |
| **故障隔离** | 单个数据库故障不影响其他服务 |
| **独立扩展** | 高负载服务可独立扩展数据库资源 |
