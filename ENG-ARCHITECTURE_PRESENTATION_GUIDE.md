# Architecture Presentation Guide

## Diagram 1: Logical Architecture Diagram

### Architecture Overview
This project adopts a **Microservices Architecture**, utilizing an API Gateway as a unified entry point to achieve service decoupling and independent deployment.

### Five-Layer Architecture Explanation

#### 1. Frontend Layer
- **Tech Stack**: Vue.js 3 + Vite
- **User Roles**: Customer, Provider (Service Provider), Admin (Administrator)
- **Location**: `frontend/src/views/` directory
- **Description**: Provides web interfaces for three roles, communicating with the backend via REST API

#### 2. API Gateway Layer
- **Tech Stack**: FastAPI (Python)
- **Port**: 8080
- **Core Functions**:
  - Route forwarding (`gateway-service/src/gateway_service/api/routes.py`)
  - JWT authentication (`core/jwt_handler.py`)
  - Rate limiting protection (`core/rate_limiter.py`)
- **Description**: Unified entry point - all frontend requests pass through the gateway for validation before being forwarded to corresponding services

#### 3. Microservices Layer
6 independent services, each with distinct responsibilities:

| Service | Port | Database | Core Responsibilities | Code Location |
|---------|------|----------|----------------------|---------------|
| **Auth Service** | 8000 | MySQL | User registration/login, JWT issuance | `services/auth-service/src/auth_service/services/auth_service.py` |
| **User Service** | 8002 | MongoDB | User profile management, Provider verification | `services/user-service/src/user_service/services/user_service.py` |
| **Order Service** | 8003 | MySQL | Order creation, status transitions, order assignment | `services/order-service/src/order_service/services/` |
| **Payment Service** | 8004 | MySQL | Payment processing, refund management | `services/payment-service/src/payment_service/services/payment_service.py` |
| **Review Service** | 8005 | MongoDB | Review submission, rating statistics | `services/review-service/src/review_service/services/review_service.py` |
| **Notification Service** | 8006 | MongoDB | Message push, event-driven notifications | `services/notification-service/src/notification_service/events/handlers/` |

#### 4. Infrastructure Layer
- **Cache**: Redis (session management, rate limiting counters)
- **Message Queue**: RabbitMQ (asynchronous event communication)
  - 5 Exchanges: `order_events`, `payment_events`, `review_events`, `auth_events`, `user_events`
  - Code example: `shared/common/messaging/message_publisher.py`

#### 5. Database Layer
**Polyglot Persistence** strategy:
- **MySQL**: Transactional data (Auth, Order, Payment)
- **MongoDB**: Flexible documents (User, Review, Notification)

---

## Diagram 2: DDD Diagram (Domain-Driven Design)

### Core Philosophy
Each service is an **independent domain** with its own models, business logic, and data storage.

### Service Domain Details

#### 1. API Gateway Service
**Responsibilities**: 
- ✅ Route requests
- ✅ Authenticate users
- ✅ Rate limiting

**Key Code**:
```python
# gateway-service/src/gateway_service/api/routes.py
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request, ...):
    # 1. JWT validation
    # 2. Route forwarding
    # 3. Rate limit check
```

#### 2. Auth Service (Authentication Domain)
**Responsibilities**:
- ✅ User registration
- ✅ Login/Logout
- ✅ JWT token management

**Core Model**:
```python
# services/auth-service/src/auth_service/models/user.py
class User(Base):
    id: int                    # User ID
    username: str              # Username
    email: str                 # Email
    password_hash: str         # Password hash
    role_id: int               # Role ID (1=Customer, 2=Provider, 3=Admin)
```

**Database**: MySQL - `auth_db` (users, roles tables)

#### 3. User Service (User Domain)
**Responsibilities**:
- ✅ Manage user profiles

**Core Features**:
- Customer: Update personal information, address, contact details
- Provider: Upload qualification certificates, set service areas, skill tags
- Admin: Review Provider qualifications

**Database**: MongoDB - `user_db` (users collection, supports flexible schema)

#### 4. Order Service (Order Domain)
**Responsibilities**:
- ✅ Create orders
- ✅ Track order status
- ✅ Manage order lifecycle
- ✅ Order details & history

**Order Status Flow**:
```
pending_review → pending → accepted → in_progress → completed → reviewed
                    ↓
                cancelled
```

**Key Code**:
```python
# services/order-service/src/order_service/models/order.py
class Order(Base):
    service_type: ServiceType   # Service type (cleaning/repair, IT, etc.)
    status: OrderStatus         # Order status
    location: Location          # Service area (NORTH/SOUTH/EAST/WEST/MID)
    payment_status: PaymentStatus  # Payment status
```

**Database**: MySQL - `order_db` (orders table)

#### 5. Payment Service (Payment Domain)
**Responsibilities**:
- ✅ Process payments
- ✅ Manage transactions

**Event-Driven**:
```python
# Publish event after payment completion
await publish_event(
    exchange="payment_events",
    routing_key="payment.completed",
    message={"order_id": order_id, "amount": amount}
)
```

**Database**: MySQL - `payment_db` (payments, refunds tables)

#### 6. Review Service (Review Domain)
**Responsibilities**:
- ✅ Submit reviews
- ✅ Rating system
- ✅ Review moderation

**Core Flow**:
1. Order completed → Allow Customer to review
2. Review includes: Rating (1-5 stars), comment content, service attitude, professionalism
3. Publish `review.created` event → Update Provider rating

**Database**: MongoDB - `review_db` (reviews collection)

#### 7. Notification Service (Notification Domain)
**Responsibilities**:
- ✅ Send order notifications
- ✅ Send admin notifications
- ✅ Event-driven messaging

**Event Consumer**:
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py
async def handle_order_created(message: dict):
    # Order created → Notify Customer and matched Providers
    
async def handle_order_accepted(message: dict):
    # Order accepted → Notify Customer and Provider
```

**Database**: MongoDB - `notification_db` (notifications collection)

---

## Diagram 3: Event-Driven Architecture

### Architecture Overview
Adopts the **Producer-Consumer pattern**, implementing asynchronous decoupled communication between services through RabbitMQ.

### Three-Layer Event Flow Structure

#### Layer 1: Event Producers
5 services act as event publishers, each publishing domain events:

**Auth Service**:
- `user.registered` - New user registration completed

**Payment Service**:
- `payment.initiated` - Payment initiated
- `payment.completed` - Payment completed
- `payment.failed` - Payment failed

**Review Service**:
- `review.created` - Review created
- `rating.updated` - Rating updated

**Order Service** (Most critical event source):
- `order.created` - Order created
- `order.accepted` - Provider accepted order
- `order.cancelled` - Order cancelled
- `order.status_changed` - Order status changed
- `order.approved` - Admin approved order
- `order.rejected` - Admin rejected order

**User Service**:
- `profile.created` - User profile created
- `profile.updated` - User profile updated

#### Layer 2: Event Bus (RabbitMQ)

**Exchange Configuration** (Topic type):
```python
# 5 Topic Exchanges, supporting routing key pattern matching
auth_events     # Routing key: user.*
payment_events  # Routing key: payment.*
review_events   # Routing key: review.*, rating.*
order_events    # Routing key: order.*
user_events     # Routing key: profile.*
```

**Queue Bindings** (3 core queues):
```python
# shared/common/messaging/message_publisher.py
payment_queue:
  - Bindings: payment.*
  - Purpose: Payment Service handles payment transactions
  
review_queue:
  - Bindings: review.*
  - Purpose: Review Service handles review logic
  
order_queue:
  - Bindings: order.*
  - Purpose: Notification Service listens to order events
```

**Actual Code Example**:
```python
# shared/common/messaging/message_publisher.py
async def publish_event(exchange: str, routing_key: str, message: dict):
    """Unified event publishing interface"""
    channel = await get_rabbitmq_channel()
    
    await channel.exchange_declare(
        exchange=exchange,
        exchange_type='topic',  # Topic type supports wildcards
        durable=True
    )
    
    await channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(message).encode(),
        properties=aiormq.spec.Basic.Properties(
            delivery_mode=2  # Persistent message
        )
    )
```

#### Layer 3: Event Consumer

**Notification Service** - The only multi-event consumer:
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py

async def handle_order_created(message: dict):
    """Order created → Notify matched Providers"""
    # 1. Query matching Providers (area, skill match)
    # 2. Create notification records
    # 3. Push to Provider's inbox

async def handle_order_accepted(message: dict):
    """Order accepted → Notify Customer and Provider"""
    # 1. Notify Customer: "Your order has been accepted"
    # 2. Notify Provider: "Please complete service on time"

async def handle_payment_completed(message: dict):
    """Payment completed → Notify both parties"""
    # 1. Notify Customer: "Payment successful"
    # 2. Notify Provider: "Funds are escrowed"

async def handle_review_created(message: dict):
    """Review created → Notify Provider"""
    # Notify Provider: "You received a new review"
```

**Subscription Configuration**:
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

### Event-Driven Advantages

✅ **Decoupling**: Order Service doesn't need to know Notification Service exists  
✅ **Asynchronous**: Order creation returns immediately, notification push happens in background  
✅ **Scalability**: Adding new Consumers requires no Producer code changes  
✅ **Fault Tolerance**: RabbitMQ persistence guarantees no message loss  
✅ **Flexible Routing**: Topic Exchange supports complex subscription patterns

### Typical Event Flow Examples

**Scenario: Customer Publishes Order**
```
1. Order Service → publish("order_events", "order.created", {...})
2. RabbitMQ → route to order_queue (binding: order.*)
3. Notification Service → consume from order_queue
4. Notification Service → Query matching Providers → Push notifications
```

**Scenario: Payment Completion Chain**
```
1. Payment Service → publish("payment_events", "payment.completed", {order_id: 123})
2. RabbitMQ → route to payment_queue
3. Order Service → Update order.payment_status = 'paid'
4. Order Service → publish("order_events", "order.status_changed", {...})
5. Notification Service → Notify Customer payment successful
```

---

## Diagram 4: Polyglot Persistence Architecture

### Architecture Overview
Select the **most appropriate database technology** based on different service data characteristics, achieving tech stack diversification.

### Two Types of Database Deployment

#### AWS RDS MySQL 8.0 (Relational Database)
Used for **transactional, high-consistency** business scenarios.

**Auth Database (MySQL)**:
- **Deployment**: AWS RDS MySQL 8.0 instance
- **ORM**: SQLAlchemy (async)
- **Table Structure**:
  ```sql
  -- users table
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
  
  -- roles table
  CREATE TABLE roles (
      id INT PRIMARY KEY AUTO_INCREMENT,
      name VARCHAR(50) UNIQUE NOT NULL  -- 'customer', 'provider', 'admin'
  );
  ```
- **Code Location**: `services/auth-service/src/auth_service/models/user.py`
- **Why MySQL**: User authentication requires ACID characteristics to prevent duplicate registration and role confusion

**Order Database (MySQL)**:
- **Deployment**: AWS RDS MySQL 8.0 instance
- **ORM**: SQLAlchemy (async)
- **Table Structure**:
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
- **Code Location**: `services/order-service/src/order_service/models/order.py`
- **Why MySQL**: Order status transitions require transaction guarantees to avoid state inconsistencies

**Payment Database (MySQL)**:
- **Deployment**: AWS RDS MySQL 8.0 instance
- **ORM**: SQLAlchemy (async)
- **Table Structure**:
  ```sql
  -- payments table
  CREATE TABLE payments (
      id BIGINT PRIMARY KEY AUTO_INCREMENT,
      order_id BIGINT NOT NULL,
      transaction_id VARCHAR(255) UNIQUE NOT NULL,
      amount DECIMAL(10,2) NOT NULL,
      status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
      payment_method VARCHAR(50),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
  
  -- transactions table (payment flow)
  CREATE TABLE transactions (
      id BIGINT PRIMARY KEY AUTO_INCREMENT,
      payment_id BIGINT NOT NULL,
      action VARCHAR(50) NOT NULL,  -- 'charge', 'refund', 'hold'
      amount DECIMAL(10,2) NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (payment_id) REFERENCES payments(id)
  );
  ```
- **Code Location**: `services/payment-service/src/payment_service/models/payment.py`
- **Why MySQL**: Payment transactions must guarantee ACID to prevent financial loss

#### MongoDB Atlas 7.0 (Document Database)
Used for **flexible schema, read-heavy** business scenarios.

**User Database (MongoDB)**:
- **Deployment**: MongoDB Atlas 7.0 cluster
- **Driver**: Motor (async MongoDB driver)
- **Collections**:
  ```javascript
  // customer_profiles collection
  {
      _id: ObjectId,
      user_id: 123,  // Links to auth_db.users.id
      full_name: "John Doe",
      phone: "13800138000",
      address: {
          province: "Beijing",
          city: "Haidian District",
          detail: "No.1 Zhongguancun Street"
      },
      preferences: {
          location: "NORTH",
          service_types: ["it_technology", "cleaning_repair"]
      },
      created_at: ISODate("2025-10-25T10:00:00Z")
  }
  
  // provider_profiles collection (more flexible schema)
  {
      _id: ObjectId,
      user_id: 456,
      full_name: "Jane Smith",
      skills: ["Network repair", "Computer assembly", "System installation"],
      certifications: [
          {name: "Computer Repair Technician", file_url: "https://..."}
      ],
      service_areas: ["NORTH", "MID"],
      rating: 4.8,
      completed_orders: 156,
      verified: true
  }
  ```
- **Code Location**: `services/user-service/src/user_service/services/user_service.py`
- **Why MongoDB**: User profile fields vary greatly (Customer vs Provider), MongoDB's flexible schema is more suitable

**Review Database (MongoDB)**:
- **Deployment**: MongoDB Atlas 7.0 cluster
- **Driver**: Motor (async)
- **Collections**:
  ```javascript
  // reviews collection
  {
      _id: ObjectId,
      order_id: 789,
      customer_id: 123,
      provider_id: 456,
      rating: 5,  // 1-5 stars
      comment: "Great service, professional and courteous",
      dimensions: {  // Multi-dimensional rating
          professionalism: 5,
          attitude: 5,
          punctuality: 4
      },
      images: ["https://...", "https://..."],
      created_at: ISODate("2025-10-25T15:00:00Z")
  }
  
  // ratings collection (aggregated statistics)
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
- **Code Location**: `services/review-service/src/review_service/services/review_service.py`
- **Why MongoDB**: Review content is diverse (text, images, multi-dimensional ratings), MongoDB is more flexible

**Notification Database (MongoDB)**:
- **Deployment**: MongoDB Atlas 7.0 cluster
- **Driver**: Motor (async)
- **Collections**:
  ```javascript
  // customer_inbox collection
  {
      _id: ObjectId,
      user_id: 123,
      type: "order_update",
      title: "Order Accepted",
      content: "Provider Jane Smith has accepted your order, please pay promptly",
      order_id: 789,
      is_read: false,
      created_at: ISODate("2025-10-25T12:00:00Z")
  }
  
  // provider_inbox collection
  {
      _id: ObjectId,
      user_id: 456,
      type: "new_order",
      title: "New Order Notification",
      content: "You have a new matching order, please check",
      order_id: 789,
      is_read: false,
      created_at: ISODate("2025-10-25T11:00:00Z")
  }
  ```
- **Code Location**: `services/notification-service/src/notification_service/services/notification_service.py`
- **Why MongoDB**: Notification messages are append-only data, MongoDB has better write performance

### Database Connection Configuration

**MySQL Connection (SQLAlchemy async)**:
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

**MongoDB Connection (Motor async)**:
```python
# services/user-service/src/user_service/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    "mongodb+srv://user:password@user-cluster.mongodb.net/user_db?retryWrites=true&w=majority"
)
db = client.user_db
```

### Polyglot Persistence Advantages

✅ **Technology Selection Freedom**: Choose optimal solution based on data characteristics  
✅ **Performance Optimization**: MySQL guarantees transactions, MongoDB improves read/write speed  
✅ **Cost Control**: MongoDB Atlas scales on demand, saving costs  
✅ **Risk Isolation**: Database failures won't affect all services  
✅ **Team Expertise**: Different teams can use familiar tech stacks

### Data Consistency Strategy

**Cross-Database Relationships**:
```python
# Example: Order Service needs Customer information
# 1. Get order.customer_id from order_db
# 2. Call User Service API to get customer details
# 3. No database-level JOIN operations
```

**Eventual Consistency**:
```python
# Example: Update order status after payment completion
# 1. Payment Service: payment.status = 'completed'
# 2. Publish event: payment.completed
# 3. Order Service: Listen to event → order.payment_status = 'paid'
# 4. Brief delay exists (milliseconds), but eventually consistent
```

---

## Inter-Service Communication Patterns

### Synchronous Communication
- **Method**: REST API
- **Scenario**: Gateway → Services, Service → Service (requires immediate response)
- **Example**: Payment Service queries Order details

### Asynchronous Communication
- **Method**: RabbitMQ events
- **Scenario**: Status change notifications, cross-service data sync
- **Examples**: 
  - `order.accepted` → Payment Service creates pending payment record
  - `payment.completed` → Order Service updates payment status
  - `order.completed` → Review Service allows reviews

---

## Key Design Patterns

### 1. API Gateway Pattern
- Unified entry point, simplifies frontend calls
- Centralized authentication and authorization
- Load balancing and rate limiting

### 2. Event-Driven Architecture
- Service decoupling, reduces dependencies
- Asynchronous processing, improves performance
- Event sourcing, facilitates auditing

### 3. Polyglot Persistence
- MySQL: ACID transaction guarantee (orders, payments)
- MongoDB: Flexible schema (user profiles, reviews)
- Redis: High-speed cache (rate limiting, sessions)

### 4. Database per Service
- Data isolation, independent scaling
- Freedom to choose tech stack
- Avoids single point of failure

---

## Presentation Tips

### Recommended Explanation Order
1. **Diagram 1 - Logical Architecture**: Top to bottom (Frontend → Gateway → Services → Infrastructure → Database)
2. **Diagram 2 - DDD Diagram**: By business flow (Auth → Order → Payment → Review → Notification)
3. **Diagram 3 - Event-Driven Architecture**: Left to right (Producers → Exchanges → Queues → Consumer)
4. **Diagram 4 - Polyglot Persistence**: By database type (MySQL transactional vs MongoDB document)
5. **Comprehensive Case**: Use "Customer Publishes Order" to connect all architecture diagrams

### Relationship Between Four Diagrams
```
Diagram 1 (Logical) - Overall architecture panorama, system layers from macro perspective
    ↓
Diagram 2 (DDD) - Microservice responsibilities refined, domain boundaries of each service
    ↓
Diagram 3 (Event-Driven) - Asynchronous communication mechanism between services, decoupling strategy
    ↓
Diagram 4 (Polyglot) - Data storage selection, tech stack diversification
```

### Key Highlights
✨ **Microservices Architecture**: 6 independent services, independently deployable and scalable  
✨ **Event-Driven**: 15+ event types, achieving service decoupling  
✨ **Multi-Database Strategy**: 3 MySQL + 3 MongoDB, selected based on needs  
✨ **API Gateway**: Unified authentication, rate limiting, routing, simplifies frontend calls  
✨ **DDD Design**: Each service is an independent domain with clear responsibility boundaries  
✨ **RabbitMQ**: 5 Exchanges + 3 Queues, flexible routing  
✨ **AWS Cloud Deployment**: RDS instances + MongoDB Atlas, high-availability architecture

### Focus Points (For Each Diagram)

**Diagram 1 Focus**: 
- Emphasize the central position of API Gateway
- Explain why Redis is used for cache, RabbitMQ for message queue
- Specify port numbers and tech stack for 6 services

**Diagram 2 Focus**:
- Core responsibilities of each service (3-4 points)
- Order Service is the business core (order status transitions)
- Notification Service is the only event consumer

**Diagram 3 Focus**:
- Producer-Consumer decoupling pattern
- Topic Exchange routing mechanism (wildcard matching)
- Example: How `order.created` flows from Order Service to Notification Service

**Diagram 4 Focus**:
- MySQL vs MongoDB selection criteria
- Why Auth/Order/Payment must use MySQL (ACID)
- Why User/Review/Notification suit MongoDB (flexible schema)
- Display actual table structures and Collection documents

### Potential Questions Preparation
**Q: Why not use monolithic architecture?**  
A: Microservices support independent deployment, flexible tech stack, parallel team development, suitable for complex business scenarios.

**Q: How to ensure data consistency between services?**  
A: Use event-driven + eventual consistency model, critical transactions guaranteed by MySQL's ACID characteristics.

**Q: What if RabbitMQ crashes?**  
A: Core flows (ordering, payment) are synchronous, notification features can degrade, RabbitMQ supports clustering and persistence.

**Q: Why do some services use MySQL and others MongoDB?**  
A: Selection based on data characteristics - transactional use MySQL (orders, payments), flexible schema use MongoDB (user profiles, reviews).

**Q: What's the difference between Event-Driven and REST API?**  
A: REST is synchronous calls (wait for response), Events are asynchronous notifications (fire and forget), each has applicable scenarios.

**Q: How many services does an order go through from creation to completion?**  
A: At least 5 - Order (creation) → Notification (notify Provider) → Payment (payment) → Order (status update) → Review (rating).

---

## Code Demonstration Paths

For live code demonstrations, recommended paths:

### Diagram 1 & 2 Related Code
1. **Gateway Routing**: `gateway-service/src/gateway_service/api/routes.py` (lines 58-89)
2. **Order Creation**: `services/order-service/src/order_service/services/customer_order_service.py` (lines 26-80)
3. **Data Models**: `services/order-service/src/order_service/models/order.py` (view complete field definitions)

### Diagram 3 (Event-Driven) Related Code
4. **Event Publisher**: `shared/common/messaging/message_publisher.py` (lines 15-32)
   ```python
   # Show how to publish events to RabbitMQ
   await publish_event(
       exchange="order_events",
       routing_key="order.created",
       message={...}
   )
   ```

5. **Event Consumer**: `services/notification-service/src/notification_service/events/consumer.py`
   ```python
   # Show how to subscribe to multiple events
   SUBSCRIPTIONS = [
       "order.created",
       "payment.completed",
       ...
   ]
   ```

6. **Event Handler**: `services/notification-service/src/notification_service/events/handlers/order_event_handler.py` (lines 20-59)
   ```python
   # Show order.created event handling logic
   async def handle_order_created(message: dict):
       # Query matching Providers
       # Create notification records
       # Push to inbox
   ```

### Diagram 4 (Polyglot Persistence) Related Code

**MySQL Related**:
7. **Auth Database Config**: `services/auth-service/src/auth_service/core/database.py`
   ```python
   # Show SQLAlchemy async engine configuration
   engine = create_async_engine(
       "mysql+aiomysql://...",
       pool_size=10
   )
   ```

8. **User Model (MySQL)**: `services/auth-service/src/auth_service/models/user.py`
   ```python
   # Show SQLAlchemy ORM model definition
   class User(Base):
       __tablename__ = "users"
       id = Column(BigInteger, primary_key=True)
       ...
   ```

9. **Order Model (MySQL)**: `services/order-service/src/order_service/models/order.py`
   ```python
   # Show ENUM field definitions
   class ServiceType(str, Enum):
       CLEANING_REPAIR = "cleaning_repair"
       IT_TECHNOLOGY = "it_technology"
       ...
   ```

**MongoDB Related**:
10. **User Database Config**: `services/user-service/src/user_service/core/database.py`
    ```python
    # Show Motor async MongoDB client
    client = AsyncIOMotorClient("mongodb+srv://...")
    db = client.user_db
    ```

11. **User Service (MongoDB Operations)**: `services/user-service/src/user_service/services/user_service.py`
    ```python
    # Show MongoDB flexible queries
    async def get_customer_profile(user_id: int):
        profile = await db.customer_profiles.find_one({"user_id": user_id})
        return profile
    ```

12. **Review Service (MongoDB Aggregation)**: `services/review-service/src/review_service/services/review_service.py`
    ```python
    # Show MongoDB aggregation pipeline
    async def calculate_provider_rating(provider_id: int):
        pipeline = [
            {"$match": {"provider_id": provider_id}},
            {"$group": {"_id": "$provider_id", "avg": {"$avg": "$rating"}}}
        ]
        result = await db.reviews.aggregate(pipeline).to_list(1)
    ```

### Recommended Demonstration Order
1. First show MySQL's strict schema (User/Order models)
2. Then show MongoDB's flexible documents (Customer/Provider profile differences)
3. Compare connection configuration code for both databases
4. Demonstrate complete event publish and consume flow
5. Finally return to architecture diagrams, summarize technology selection rationale

---

## Comprehensive Case Study: Customer Publishes Order - Complete Flow

Connect all 4 architecture diagrams through a complete business process.

### Business Scenario
Customer John Doe publishes a "Computer Repair" order, expecting Provider Jane Smith to accept and complete the service.

### Detailed Flow (Combining 4 Diagrams)

#### Phase 1: User Authentication (Diagram 1 + 2)

**Frontend Operation**:
```javascript
// Frontend (Vue.js)
POST http://localhost:8080/api/auth/login
{
  "username": "johndoe",
  "password": "password123"
}
```

**Architecture Flow**:
```
Frontend (Diagram 1-Layer1) 
  → API Gateway (Diagram 1-Layer2, Diagram 2-Gateway Service)
    → Auth Service (Diagram 1-Layer3, Diagram 2-Auth Service)
      → MySQL auth_db (Diagram 1-Layer5, Diagram 4-Auth Database)
```

**Database Operation (Diagram 4 - MySQL)**:
```sql
-- Auth Service queries user
SELECT id, username, password_hash, role_id 
FROM users 
WHERE username = 'johndoe';

-- After password verification, return JWT Token
```

**Return Result**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": 123,
  "role": "customer"
}
```

---

#### Phase 2: Create Order (Diagram 1 + 2 + 4)

**Frontend Operation**:
```javascript
// Frontend
POST http://localhost:8080/api/orders/
Headers: { "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..." }
{
  "service_type": "it_technology",
  "location": "NORTH",
  "description": "Computer won't boot, needs repair",
  "amount": 200.00
}
```

**Architecture Flow**:
```
Frontend 
  → API Gateway (JWT validation + rate limit check)
    → Order Service (Diagram 2-Order Service)
      → MySQL order_db (Diagram 4-Order Database)
```

**Order Service Code**:
```python
# services/order-service/src/order_service/services/customer_order_service.py
async def publish_order(customer_id: int, order_data: dict):
    # 1. Create order (status: pending_review)
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
    
    # 2. Publish event (Diagram 3 - Event-Driven)
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

**Database Operation (Diagram 4 - MySQL)**:
```sql
-- Order Database
INSERT INTO orders 
(customer_id, service_type, location, status, payment_status, amount, created_at)
VALUES 
(123, 'it_technology', 'NORTH', 'pending_review', 'unpaid', 200.00, NOW());
```

---

#### Phase 3: Event-Driven Notification (Diagram 3 - Event-Driven)

**Event Publishing (Producer)**:
```
Order Service 
  → publish to RabbitMQ
    → Exchange: order_events (Topic)
      → Routing Key: order.created
```

**RabbitMQ Routing (Diagram 3 - Event Bus)**:
```
order_events Exchange 
  → route to order_queue (binding: order.*)
    → Notification Service subscribes to order_queue
```

**Event Consumption (Consumer)**:
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py
async def handle_order_created(message: dict):
    order_id = message['order_id']
    location = message['location']
    service_type = message['service_type']
    
    # 1. Query matching Providers (Diagram 4 - MongoDB)
    providers = await db.provider_profiles.find({
        "service_areas": location,
        "skills": {"$in": ["Computer repair", "Hardware repair"]},
        "verified": True
    }).to_list(10)
    
    # 2. Create notification records
    for provider in providers:
        notification = {
            "user_id": provider['user_id'],
            "type": "new_order",
            "title": "New Order Notification",
            "content": f"You have a new {service_type} order",
            "order_id": order_id,
            "is_read": False,
            "created_at": datetime.utcnow()
        }
        await db.provider_inbox.insert_one(notification)
    
    # 3. Notify Customer
    await db.customer_inbox.insert_one({
        "user_id": message['customer_id'],
        "type": "order_created",
        "title": "Order Created Successfully",
        "content": "Your order has been published, waiting for Provider to accept",
        "order_id": order_id,
        "is_read": False,
        "created_at": datetime.utcnow()
    })
```

**Database Operation (Diagram 4 - MongoDB)**:
```javascript
// Notification Database - MongoDB
db.provider_inbox.insertMany([
    {
        user_id: 456,  // Provider Jane Smith
        type: "new_order",
        title: "New Order Notification",
        order_id: 789,
        is_read: false,
        created_at: ISODate("2025-10-25T10:00:00Z")
    },
    // ... other matching Providers
]);

db.customer_inbox.insertOne({
    user_id: 123,  // Customer John Doe
    type: "order_created",
    title: "Order Created Successfully",
    order_id: 789,
    is_read: false
});
```

---

#### Phase 4: Provider Accepts Order (Diagram 1 + 2 + 3 + 4)

**Provider Operation**:
```javascript
// Provider Jane Smith views notification and decides to accept
PUT http://localhost:8080/api/orders/789/accept
Headers: { "Authorization": "Bearer <provider_token>" }
```

**Order Service Code**:
```python
# services/order-service/src/order_service/services/provider_order_service.py
async def accept_order(order_id: int, provider_id: int):
    # 1. Update order (Diagram 4 - MySQL)
    order = await db.get(Order, order_id)
    order.provider_id = provider_id
    order.status = OrderStatus.ACCEPTED
    await db.commit()
    
    # 2. Publish event (Diagram 3)
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

**Database Update (Diagram 4 - MySQL)**:
```sql
UPDATE orders 
SET provider_id = 456, status = 'accepted', updated_at = NOW()
WHERE id = 789;
```

**Event Flow (Diagram 3)**:
```
Order Service → order_events Exchange → order_queue → Notification Service
```

**Notification Processing**:
```python
async def handle_order_accepted(message: dict):
    # Notify Customer
    await db.customer_inbox.insert_one({
        "user_id": message['customer_id'],
        "type": "order_accepted",
        "title": "Order Accepted",
        "content": "Provider has accepted your order, please pay promptly",
        "order_id": message['order_id']
    })
    
    # Notify Provider
    await db.provider_inbox.insert_one({
        "user_id": message['provider_id'],
        "type": "order_accepted",
        "title": "Order Accepted Successfully",
        "content": "You have successfully accepted the order, waiting for Customer payment",
        "order_id": message['order_id']
    })
```

---

#### Phase 5: Payment Process (Diagram 2 + 3 + 4)

**Customer Payment**:
```javascript
POST http://localhost:8080/api/payments/
{
  "order_id": 789,
  "amount": 200.00,
  "payment_method": "alipay"
}
```

**Payment Service Code**:
```python
# services/payment-service/src/payment_service/services/payment_service.py
async def process_payment(order_id: int, amount: Decimal):
    # 1. Create payment record (Diagram 4 - MySQL)
    payment = Payment(
        order_id=order_id,
        amount=amount,
        status=PaymentStatus.PENDING,
        transaction_id=generate_transaction_id()
    )
    db.add(payment)
    await db.commit()
    
    # 2. Call third-party payment API (Alipay)
    result = await alipay_api.charge(
        amount=amount,
        transaction_id=payment.transaction_id
    )
    
    # 3. Update payment status
    if result.success:
        payment.status = PaymentStatus.COMPLETED
        await db.commit()
        
        # 4. Publish event (Diagram 3)
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

**Database Operation (Diagram 4 - MySQL)**:
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

**Event Chain (Diagram 3)**:
```
Payment Service → payment_events Exchange → payment_queue 
  → Order Service listens → update order.payment_status = 'paid'
  → Notification Service listens → notify Customer and Provider
```

---

### Complete Flow Summary

```
1. Frontend Layer (Diagram 1-Layer1)
   └─ Customer login → create order

2. Gateway Layer (Diagram 1-Layer2)
   └─ JWT validation → rate limit check → route forwarding

3. Microservices Layer (Diagram 1-Layer3, Diagram 2 all services)
   ├─ Auth Service: user authentication
   ├─ Order Service: order creation, status management
   ├─ Payment Service: payment processing
   └─ Notification Service: message push

4. Infrastructure Layer (Diagram 1-Layer4)
   ├─ Redis: rate limit counting, session cache
   └─ RabbitMQ: event-driven communication (Diagram 3)
       ├─ 5 Exchanges: order_events, payment_events, ...
       ├─ 3 Queues: order_queue, payment_queue, review_queue
       └─ 15+ events: order.created, order.accepted, payment.completed, ...

5. Database Layer (Diagram 1-Layer5, Diagram 4)
   ├─ MySQL (3 instances - AWS RDS)
   │   ├─ auth_db: user authentication data
   │   ├─ order_db: order transaction data
   │   └─ payment_db: payment transaction data
   └─ MongoDB (3 clusters - Atlas)
       ├─ user_db: user profiles (flexible schema)
       ├─ review_db: review data
       └─ notification_db: notification messages (append-only)
```

### Technical Highlights

✅ **Microservices Decoupling (Diagram 2)**: 6 services independently developed and deployed  
✅ **Event-Driven (Diagram 3)**: Order status changes automatically trigger notifications without explicit calls  
✅ **Multi-Database (Diagram 4)**: Orders use MySQL for ACID guarantee, notifications use MongoDB for performance  
✅ **API Gateway (Diagram 1)**: Unified entry point, simplifies frontend calls  
✅ **Asynchronous Processing (Diagram 3)**: Notification push doesn't block order creation, improves response speed

---

## Diagram 5: Customer Publish Order Sequence Diagram

### Process Overview
Displays the **complete interaction flow** from Customer initiating an order creation request from the frontend, through Gateway authentication, Order Service processing, database storage, event publishing, to final notification push.

### 15-Step Detailed Flow

#### Step 1-2: Frontend Initiates Request
```javascript
// Frontend - Customer clicks "Publish Order" button
POST http://localhost:8080/api/customer/orders/publish
Headers: {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
}
Body: {
  "title": "Computer Repair",
  "description": "Computer won't boot, needs repair",
  "service_type": "it_technology",
  "price": 200.00,
  "location": "NORTH",
  "address": "No.1 Zhongguancun Street, Haidian District, Beijing"
}
```

**Key Points**: 
- Customer is logged in, carries JWT Token
- Request sent to API Gateway's unified entry (port 8080)

---

#### Step 3-4: API Gateway Authentication
```python
# gateway-service/src/gateway_service/api/routes.py
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request, ...):
    # Step 3: Validate JWT Token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Step 4: Call Auth Service to verify Token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{AUTH_SERVICE_URL}/verify-token",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    user_data = response.json()  # {user_id: 123, role: "customer"}
    
    # Inject user_id into request header, forward to Order Service
    request.state.user_id = user_data["user_id"]
```

**Key Points**:
- Gateway doesn't directly validate Token, but calls Auth Service
- After successful validation, extracts user_id and injects into subsequent requests

---

#### Step 5-6: Order Service Creates Order
```python
# services/order-service/src/order_service/services/customer_order_service.py
@staticmethod
async def publish_order(
    db: AsyncSession,
    customer_id: int,  # From Gateway-injected user_id
    title: str,
    description: str,
    service_type: str,
    price: float,
    location: str,
    address: str,
    service_start_time: Optional[datetime] = None,
    service_end_time: Optional[datetime] = None,
) -> Order:
    """Publish order - status is pending_review, awaiting admin approval"""
    
    # Step 5: Create order object
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
    # At this point order status defaults to: OrderStatus.pending_review
    
    # Step 6: Get Customer profile from User Service (for subsequent notifications)
    async with httpx.AsyncClient() as client:
        profile = await client.get(
            f"{USER_SERVICE_URL}/customers/{customer_id}/profile"
        )
    
    return order
```

**Key Points**:
- Order initial status is `pending_review` (requires admin approval)
- Needs to call User Service to get Customer details

---

#### Step 7-8: Database Persistence
```python
# services/order-service/src/order_service/dao/order_dao.py
@staticmethod
async def create_order(db: AsyncSession, ...) -> Order:
    # Step 7: Create Order instance
    order = Order(
        customer_id=customer_id,
        title=title,
        description=description,
        service_type=service_type,
        price=price,
        location=location,
        address=address,
        status=OrderStatus.pending_review,  # Default status
        payment_status=PaymentStatus.unpaid,  # Unpaid
        created_at=datetime.now(UTC),
    )
    
    # Step 8: Insert into database (Diagram 4 - MySQL order_db)
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    return order  # Return order object with id
```

**Database Operation (MySQL)**:
```sql
INSERT INTO orders (
    customer_id, title, description, service_type, 
    price, location, address, status, payment_status, created_at
) VALUES (
    123, 'Computer Repair', 'Computer won''t boot, needs repair', 'it_technology',
    200.00, 'NORTH', 'No.1 Zhongguancun Street, Haidian District, Beijing', 'pending_review', 'unpaid', NOW()
);
```

---

#### Step 9-10: Event Publishing (Diagram 3 - Event-Driven)
```python
# services/order-service/src/order_service/services/customer_order_service.py (continued)
    # Step 9: After order saved successfully, publish event
    event = OrderCreatedEvent(
        order_id=order.id,  # Database-generated order ID
        customer_id=customer_id,
        title=title,
        price=price,
        location=location,
        timestamp=datetime.now(UTC),
    )
    
    # Step 10: Send to RabbitMQ
    await EventPublisher.publish_order_created(event)
    
    return order
```

**Event Publishing Code**:
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
    
    # Publish to RabbitMQ's order_events Exchange
    await publish_event(
        exchange="order_events",
        routing_key="order.created",  # Routing key
        message=message
    )
```

**RabbitMQ Routing (Diagram 3)**:
```
Order Service (Producer)
  → order_events Exchange (Topic)
    → Routing Key: "order.created"
      → order_queue (Binding: order.*)
        → Notification Service (Consumer)
```

---

#### Step 11-12: Notification Service Processes Event
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py
async def handle_order_created(message: dict):
    """Handle order created event"""
    order_id = message['order_id']
    customer_id = message['customer_id']
    location = message['location']
    title = message['title']
    price = message['price']
    
    # Step 11: Cache notification to Redis (optional, improves performance)
    await redis_client.setex(
        f"notification:order:{order_id}",
        3600,  # Expires in 1 hour
        json.dumps(message)
    )
    
    # Step 12: Query matching Providers (Diagram 4 - MongoDB)
    # Criteria: service area match, skill match, verified
    providers = await db.provider_profiles.find({
        "service_areas": {"$in": [location]},  # Service area includes NORTH
        "skills": {"$regex": "computer|repair|IT", "$options": "i"},  # Skill match
        "verified": True,  # Verified
        "is_active": True  # Account active
    }).to_list(20)  # Notify up to 20 Providers
    
    # Step 13: Create notification records (Diagram 4 - MongoDB)
    notifications = []
    for provider in providers:
        notification = {
            "user_id": provider['user_id'],
            "type": "new_order",
            "title": "New Order Notification",
            "content": f"You have a new order: {title} (¥{price})",
            "order_id": order_id,
            "location": location,
            "is_read": False,
            "created_at": datetime.now(UTC)
        }
        notifications.append(notification)
    
    if notifications:
        await db.provider_inbox.insert_many(notifications)
    
    # Also notify Customer of order creation success
    await db.customer_inbox.insert_one({
        "user_id": customer_id,
        "type": "order_created",
        "title": "Order Created Successfully",
        "content": f"Your order \"{title}\" has been published, awaiting admin approval",
        "order_id": order_id,
        "is_read": False,
        "created_at": datetime.now(UTC)
    })
```

---

#### Step 13-14: Return Response
```python
# Step 13: Order Service returns order data to Gateway
return {
    "order_id": order.id,
    "status": "pending_review",
    "message": "Order created successfully, awaiting approval"
}

# Step 14: Gateway returns to Frontend
# Step 15: Frontend displays success message
```

**Frontend Display**:
```javascript
// Frontend receives response
{
    "order_id": 789,
    "status": "pending_review",
    "message": "Order created successfully, awaiting approval"
}

// Show alert
alert("Order published successfully! Order #789");
// Navigate to order list page
router.push('/customer/orders');
```

---

### Flow Summary

```
1. Customer → Frontend → POST /api/customer/orders/publish
2. Frontend → API Gateway (JWT Token validation)
3. API Gateway → Auth Service (verify Token)
4. Auth Service → API Gateway (return user_id)
5. API Gateway → Order Service (forward request + user_id)
6. Order Service → User Service (get Customer profile)
7. User Service → Order Service (return profile)
8. Order Service → MySQL (insert order record)
9. MySQL → Order Service (return order_id)
10. Order Service → RabbitMQ (publish order.created event)
11. RabbitMQ → Notification Service (route event)
12. Notification Service → Redis (cache notification)
13. Notification Service → MongoDB (insert notification records)
14. Order Service → API Gateway (return success response)
15. API Gateway → Frontend (return order information)
```

### Key Technical Points

✅ **JWT Authentication**: Gateway unified verification, avoiding duplicate authentication in each service  
✅ **Sync + Async**: Order creation is synchronous (immediate return), notification push is asynchronous (background processing)  
✅ **Event-Driven**: Order Service doesn't directly call Notification Service, decoupled through events  
✅ **Database Selection**: Orders use MySQL (ACID), notifications use MongoDB (high concurrent writes)  
✅ **Intelligent Matching**: Notification Service intelligently matches Providers based on location and skills

---

## Diagram 6: Provider Accept Order Sequence Diagram

### Process Overview
Demonstrates the **complete interaction flow** when a Provider sees a new order in the notification list and clicks to accept it, including how the system updates order status, validates permissions, publishes events, and notifies both parties.

### 15-Step Detailed Flow

#### Step 1-2: Provider Initiates Accept Order Request
```javascript
// Frontend - Provider clicks "Accept" in "Available Orders" list
PUT http://localhost:8080/api/provider/orders/789/accept
Headers: {
  "Authorization": "Bearer <provider_token>"
}
```

**Preconditions**:
- Provider is logged in (role = 'provider')
- Order status must be `pending` (approved by admin)

---

#### Step 3-4: API Gateway Authentication
```python
# gateway-service/src/gateway_service/api/routes.py
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(path: str, request: Request, ...):
    # Step 3: Verify JWT Token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Step 4: Verify Token and check role
    user_data = await verify_token_with_auth_service(token)
    
    # Check if Provider role
    if user_data["role"] != "provider":
        raise HTTPException(
            status_code=403, 
            detail="Only providers can accept orders"
        )
    
    # Inject provider_id
    request.state.user_id = user_data["user_id"]
    request.state.role = user_data["role"]
```

---

#### Step 5: Order Service Handles Accept Order Request
```python
# services/order-service/src/order_service/services/provider_order_service.py
@staticmethod
async def accept_order(db: AsyncSession, provider_id: int, order_id: int) -> Order:
    """Accept order"""
    
    # Step 5: Query order
    order = await OrderDAO.get_order_by_id(db, order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found"
        )
    
    # Verify order status (only accept pending orders)
    if order.status != OrderStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="The order has already been accepted!"
        )
    
    # Step 6: Check order status (read from DB)
    # Ensure order hasn't been accepted by another Provider
    return order
```

---

#### Step 6-7: Validate and Update Order
```python
# services/order-service/src/order_service/dao/order_dao.py
@staticmethod
async def accept_order(db: AsyncSession, order_id: int, provider_id: int) -> Order:
    """Accept order - atomic operation"""
    
    # Step 7: Update order (MySQL transaction guarantee)
    result = await db.execute(
        update(Order)
        .where(Order.id == order_id)
        .where(Order.status == OrderStatus.pending)  # Optimistic lock
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
    
    # Re-query order
    order = await db.get(Order, order_id)
    return order
```

**SQL Operation (MySQL - Diagram 4)**:
```sql
-- Atomic update (WHERE ensures only pending status updates)
UPDATE orders 
SET 
    provider_id = 456,  -- Provider Li
    status = 'accepted',
    updated_at = NOW()
WHERE 
    id = 789 
    AND status = 'pending';  -- Optimistic lock: only pending can update

-- If rowcount = 0, order has been accepted by another Provider
```

---

#### Step 8-9: Publish Order Accepted Event
```python
# services/order-service/src/order_service/services/provider_order_service.py (continued)
    # Step 8: Order update successful
    updated_order = await OrderDAO.accept_order(db, order_id, provider_id)
    
    # Step 9: Publish order.accepted event (Diagram 3)
    event = OrderAcceptedEvent(
        order_id=order_id,
        customer_id=order.customer_id,  # Customer Zhang
        provider_id=provider_id,  # Provider Li
        timestamp=datetime.now(UTC)
    )
    await EventPublisher.publish_order_accepted(event)
    
    return updated_order
```

**Event Publishing**:
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

#### Step 10-11: Notification Service Handles Event
```python
# services/notification-service/src/notification_service/events/handlers/order_event_handler.py
async def handle_order_accepted(message: dict):
    """Handle order accepted event"""
    order_id = message['order_id']
    customer_id = message['customer_id']
    provider_id = message['provider_id']
    
    # Step 10: Send order.accepted event to Notification Service
    
    # Step 11: Cache notification to Redis
    await redis_client.setex(
        f"notification:order:accepted:{order_id}",
        3600,
        json.dumps(message)
    )
    
    # Step 12: Create notification (Diagram 4 - MongoDB)
    
    # Notify Customer
    customer_notification = {
        "user_id": customer_id,
        "type": "order_accepted",
        "title": "Order Accepted",
        "content": "Your order has been accepted by the provider, please pay on time",
        "order_id": order_id,
        "provider_id": provider_id,
        "is_read": False,
        "created_at": datetime.now(UTC)
    }
    await db.customer_inbox.insert_one(customer_notification)
    
    # Notify Provider
    provider_notification = {
        "user_id": provider_id,
        "type": "order_accepted",
        "title": "Order Accepted Successfully",
        "content": "You have successfully accepted the order, please wait for customer payment",
        "order_id": order_id,
        "customer_id": customer_id,
        "is_read": False,
        "created_at": datetime.now(UTC)
    }
    await db.provider_inbox.insert_one(provider_notification)
```

**MongoDB Insert (Diagram 4)**:
```javascript
// customer_inbox collection
{
    user_id: 123,  // Customer Zhang
    type: "order_accepted",
    title: "Order Accepted",
    content: "Your order has been accepted by the provider, please pay on time",
    order_id: 789,
    provider_id: 456,
    is_read: false,
    created_at: ISODate("2025-10-25T12:00:00Z")
}

// provider_inbox collection
{
    user_id: 456,  // Provider Li
    type: "order_accepted",
    title: "Order Accepted Successfully",
    content: "You have successfully accepted the order, please wait for customer payment",
    order_id: 789,
    customer_id: 123,
    is_read: false,
    created_at: ISODate("2025-10-25T12:00:00Z")
}
```

---

#### Step 13-15: Return Response
```python
# Step 13: Order Service returns updated order
return {
    "order_id": order.id,
    "status": "accepted",
    "provider_id": provider_id,
    "message": "Order accepted successfully"
}

# Step 14: API Gateway forwards response
# Step 15: Frontend displays success message
```

**Frontend Display**:
```javascript
// Provider side
{
    "order_id": 789,
    "status": "accepted",
    "provider_id": 456,
    "message": "Order accepted successfully"
}

// Show alert
alert("Order accepted successfully! Please wait for customer payment");
// Redirect to "My Orders" page
router.push('/provider/my-orders');
```

---

### Flow Summary

```
1. Provider → Frontend → PUT /api/provider/orders/789/accept
2. Frontend → API Gateway (JWT Token verification)
3. API Gateway → Auth Service (Verify Token + role check)
4. Auth Service → API Gateway (Return provider_id + role)
5. API Gateway → Order Service (Forward request + provider_id)
6. Order Service → MySQL (Query order status)
7. MySQL → Order Service (Return order: status=pending)
8. Order Service → MySQL (Atomic update: provider_id + status=accepted)
9. MySQL → Order Service (Update confirmation)
10. Order Service → RabbitMQ (Publish order.accepted event)
11. RabbitMQ → Notification Service (Route event)
12. Notification Service → Redis (Cache notification)
13. Notification Service → MongoDB (Insert notifications for both parties)
14. Order Service → API Gateway (Return success response)
15. API Gateway → Frontend (Return order information)
```

### Key Technical Points

✅ **Optimistic Lock**: Using `WHERE status = 'pending'` to prevent duplicate acceptance  
✅ **Atomic Operation**: MySQL transaction guarantees provider_id and status are updated together  
✅ **Role Validation**: Gateway checks role in JWT, only Provider can accept orders  
✅ **Event Notification**: Successful acceptance automatically notifies both Customer and Provider  
✅ **Idempotency**: If order is already accepted, return 400 error instead of 500

---

### Comparison Between Two Sequence Diagrams

| Comparison Item | Customer Publish Order | Provider Accept Order |
|----------------|------------------------|----------------------|
| **Triggering Role** | Customer | Provider |
| **Core Operation** | Create order (INSERT) | Update order (UPDATE) |
| **Initial Status** | None → pending_review | pending → accepted |
| **Concurrency Issue** | None (new order creation) | Yes (multiple Providers competing) |
| **Solution** | No special handling needed | Optimistic lock (WHERE status = 'pending') |
| **Event Published** | order.created | order.accepted |
| **Notification Target** | Matched Providers (batch) | Customer + Provider (bidirectional) |
| **Database Operation** | MySQL INSERT + MongoDB batch insert | MySQL UPDATE + MongoDB double record insert |
| **Business Complexity** | Medium (need to query User profile) | High (need to prevent duplicate acceptance) |

---

### Presentation Tips (Sequence Diagram Explanation)

**Explanation Order**:
1. **First explain Diagram 5 (Publish Order)**: Simpler flow, easier to understand from user perspective
2. **Then explain Diagram 6 (Accept Order)**: Focus on concurrency control and optimistic locking
3. **Compare both diagrams**: Emphasize INSERT vs UPDATE, unidirectional vs bidirectional notification

**Key Demonstration Points**:
- **Diagram 5 Focus**: Show how event-driven intelligently matches Providers
- **Diagram 6 Focus**: Show how MySQL optimistic lock prevents duplicate acceptance
- **Code Demo**: 
  - `customer_order_service.py`'s `publish_order` method
  - `provider_order_service.py`'s `accept_order` method
  - `order_event_handler.py`'s event handling logic

**Possible Questions**:
**Q: What happens if two Providers click accept simultaneously?**  
A: MySQL's `WHERE status = 'pending'` optimistic lock ensures only one UPDATE succeeds, the other returns rowcount=0 and throws 400 error.

**Q: If RabbitMQ goes down, will notifications be lost?**  
A: RabbitMQ is configured with `durable=True` and `delivery_mode=2`, messages are persisted to disk and automatically recovered after restart.

**Q: Why not use Redis to store orders instead of MySQL?**  
A: Orders are core business data requiring ACID transactions to guarantee (prevent amount errors, status inconsistencies). Redis is only used for caching and rate limiting.

---

## Diagram 7: Logical Detail Deployment Diagram

### Deployment Architecture Overview

This diagram uses **UML Deployment Diagram** standards to show the deployment topology of system components in physical/virtual environments, focusing on "**what components are deployed where**" rather than internal implementation details.

### UML Stereotypes Explanation

In UML deployment diagrams, stereotypes are used to identify different types of deployment elements:

| Stereotype | Meaning | Description | Example in Diagram |
|-----------|---------|-------------|-------------------|
| `<<location>>` | Deployment location/network zone | Represents network boundary or logical area | Internet, AWS Cloud |
| `<<execution environment>>` | Execution environment | Represents environment container running software | Frontend Server, Microservices Cluster |
| `<<device>>` | Physical device | Represents client hardware device | Client PC |
| `<<artifact>>` | Software artifact | Represents deployable software package/JAR/WAR | gateway-service.jar, Frontend UI |
| `<<database>>` | Database instance | Represents database server | auth_db (MySQL), user_db (MongoDB) |
| `<<node>>` | Infrastructure node | Represents middleware or infrastructure service | RabbitMQ, Redis |

### Deployment Layer Structure

#### **1️⃣ Internet Layer (<<location>>)**

**Deployment Elements**:
- **Client PC (<<device>>)**: Users access system through browser
  - **Browser**: Chrome, Safari, Firefox
  - **Protocol**: HTTPS (port 443)
  - **Connection**: Access Frontend UI in AWS Cloud via Internet

**Description**: This is the system's external boundary, representing all internet user access entry points.

---

#### **2️⃣ AWS Cloud Layer (<<location>>)**

This is the system's core deployment area, containing all application servers, middleware, and databases.

##### **Frontend Server (<<execution environment>>)**

**Deployment Artifact**: `Frontend UI (Vue.js + Vite)`  
**Port**: 80 (HTTP), 443 (HTTPS)  
**Technology Stack**: 
- Vue.js 3 (frontend framework)
- Vite (build tool)
- Nginx (web server for serving static files)

**Code Location**: `frontend/src/`

**Responsibilities**:
- Provide web interfaces for three roles (Customer, Provider, Admin)
- Static resource hosting (HTML, CSS, JS, Images)
- Call API Gateway via AJAX

**Actual Deployment Method**:
```bash
# Build frontend
cd frontend
npm run build  # Generate dist/ directory

# Deploy to Nginx
# dist/ directory content → /var/www/html/
# Nginx configuration → /etc/nginx/sites-available/frontend.conf
```

---

##### **API Gateway (<<execution environment>>)**

**Deployment Artifact**: `gateway-service.jar (FastAPI)`  
**Port**: 8080  
**Technology Stack**: FastAPI (Python) + Uvicorn (ASGI server)

**Core Components**:
- **Router**: Routing and forwarding logic
- **JWT Handler**: Token verification
- **Rate Limiter**: Redis-based rate limiting
- **Middleware**: CORS, logging, exception handling

**Code Location**: `gateway-service/src/gateway_service/`

**Responsibilities**:
- Unified API entry point (all frontend requests go through here)
- JWT authentication (verify user identity and permissions)
- Route forwarding (route requests to corresponding microservices)
- Rate limiting protection (prevent malicious attacks)

**Actual Deployment Command**:
```bash
cd gateway-service
uvicorn gateway_service.main:app --host 0.0.0.0 --port 8080 --app-dir src
```

---

##### **Microservices Cluster (<<execution environment>>)**

6 independently deployed microservices, each an **independent FastAPI application**:

| Service | Artifact | Port | Database | Technology | Code Path |
|---------|----------|------|----------|------------|-----------|
| **Auth Service** | auth-service.jar | 8000 | MySQL (auth_db) | FastAPI + SQLAlchemy | `services/auth-service/src/` |
| **User Service** | user-service.jar | 8002 | MongoDB (user_db) | FastAPI + Motor | `services/user-service/src/` |
| **Order Service** | order-service.jar | 8003 | MySQL (order_db) | FastAPI + SQLAlchemy | `services/order-service/src/` |
| **Payment Service** | payment-service.jar | 8004 | MySQL (payment_db) | FastAPI + SQLAlchemy | `services/payment-service/src/` |
| **Review Service** | review-service.jar | 8005 | MongoDB (review_db) | FastAPI + Motor | `services/review-service/src/` |
| **Notification Service** | notification-service.jar | 8006 | MongoDB (notification_db) | FastAPI + Motor | `services/notification-service/src/` |

**Deployment Characteristics**:
- ✅ **Independent Deployment**: Each service can be started/stopped/updated independently
- ✅ **Independent Database**: Each service has its own database (Database per Service pattern)
- ✅ **Stateless**: All services are stateless, easy to scale horizontally
- ✅ **Port Isolation**: Each service listens on different port, avoiding conflicts

**Actual Deployment Example (Order Service)**:
```bash
cd services/order-service
uvicorn order_service.main:app --reload --host 0.0.0.0 --port 8003 --app-dir src
```

---

##### **Infrastructure Layer**

###### **RabbitMQ (<<node>>)**

**Technology**: RabbitMQ 3.x (Message Broker)  
**Ports**: 
- 5672 (AMQP protocol, application connection)
- 15672 (Management UI, admin interface)

**Responsibilities**:
- **Message Queue**: Implement asynchronous event communication
- **Exchange Type**: Topic Exchange (supports flexible routing)
- **Exchanges**: 
  - `order_events` (order events)
  - `payment_events` (payment events)
  - `review_events` (review events)
  - `auth_events` (authentication events)
  - `user_events` (user events)

**Consumers**: 
- Notification Service subscribes to all queues, receives events and sends notifications

**Configuration Location**: `infrastructure/rabbitmq/definitions.json`

**Actual Deployment**:
```bash
# Docker method
docker run -d --name rabbitmq \
  -p 5672:5672 -p 15672:15672 \
  -v ./infrastructure/rabbitmq:/etc/rabbitmq \
  rabbitmq:3-management
```

---

###### **Redis (<<node>>)**

**Technology**: Redis 7.x (In-Memory Cache)  
**Port**: 6379

**Use Cases**:
1. **Rate Limiting**: API Gateway uses Redis counters
   - Key format: `rate_limit:{user_id}:{endpoint}`
   - Expiration time: 60 seconds
   
2. **Session Cache**: 
   - JWT Token blacklist
   - User permission cache
   
3. **Notification Cache**:
   - Unread notification count
   - Recent notifications quick query

**Code Example**:
```python
# gateway-service/src/gateway_service/core/rate_limiter.py
async def check_rate_limit(user_id: int, endpoint: str):
    key = f"rate_limit:{user_id}:{endpoint}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)  # 60 second window
    return count <= 100  # Maximum 100 requests per minute
```

**Actual Deployment**:
```bash
# Docker method
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

---

##### **Database Layer**

###### **MySQL 8.0 (<<database>>) - AWS RDS Multi-AZ**

**Deployment Method**: AWS RDS (managed database service)  
**High Availability**: Multi-AZ (dual availability zone, automatic failover)  
**Backup**: Automatic backup (7-day retention)

**Database Instances**:

| Database | Service | Table Structure | Connection String Example |
|----------|---------|----------------|---------------------------|
| **auth_db** | Auth Service | `users`, `roles` | `mysql+aiomysql://user:pass@auth-db.rds.amazonaws.com:3306/auth_db` |
| **order_db** | Order Service | `orders` | `mysql+aiomysql://user:pass@order-db.rds.amazonaws.com:3306/order_db` |
| **payment_db** | Payment Service | `payments`, `refunds` | `mysql+aiomysql://user:pass@payment-db.rds.amazonaws.com:3306/payment_db` |

**Why Choose MySQL?**
- ✅ **ACID Transactions**: Orders, payments, authentication require strong consistency
- ✅ **Foreign Key Constraints**: Ensure data integrity (e.g., user_id must exist)
- ✅ **Complex Queries**: Support JOIN, subqueries, aggregate functions
- ✅ **Mature Ecosystem**: SQLAlchemy ORM, Alembic migration tool

**Actual Connection Code**:
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

**Deployment Method**: MongoDB Atlas (cloud managed service)  
**High Availability**: 3-node Replica Set  
**Backup**: Continuous Backup (point-in-time recovery)

**Database Instances**:

| Database | Service | Collections | Connection String Example |
|----------|---------|-------------|---------------------------|
| **user_db** | User Service | `customer_profiles`, `provider_profiles` | `mongodb+srv://user:pass@user-cluster.mongodb.net/user_db` |
| **review_db** | Review Service | `reviews`, `ratings` | `mongodb+srv://user:pass@review-cluster.mongodb.net/review_db` |
| **notification_db** | Notification Service | `customer_inbox`, `provider_inbox` | `mongodb+srv://user:pass@notification-cluster.mongodb.net/notification_db` |

**Why Choose MongoDB?**
- ✅ **Flexible Schema**: User profiles can extend fields anytime (skills, portfolios)
- ✅ **Nested Documents**: Provider's availability schedule can be stored as nested objects
- ✅ **High Concurrent Writes**: Notification service needs frequent message inserts
- ✅ **Full-Text Search**: Review content supports text search

**Actual Connection Code**:
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

### Communication Pattern Details

| Connection Type | Diagram Representation | Description | Example |
|----------------|----------------------|-------------|---------|
| **Solid Arrow** `---` | Synchronous HTTP call | Request-response pattern, wait for result | Client → Frontend, Gateway → Services, Services → Database |
| **Dashed Arrow** `-.->` | Deployment relationship/cache access | Represents "deployed on" or "uses" | Services -.-> Redis (uses cache) |
| **Bold Arrow** `==>` | Asynchronous message communication | Publish events via RabbitMQ | Services ==> RabbitMQ ==> Notification |

**Synchronous Call Example (HTTP)**:
```
Frontend → API Gateway → Order Service → MySQL
  (HTTPS)     (HTTP)          (SQL)
```

**Asynchronous Communication Example (Events)**:
```
Order Service → RabbitMQ (order.created) → Notification Service
    (Publish)        (Route)              (Consume + Send Email)
```

---

### Deployment Architecture Features

#### **1️⃣ Architecture Style**: Microservices
- 7 independent services (1 Gateway + 6 Microservices)
- Each service deployed and scaled independently
- Services communicate via REST API and message queue

#### **2️⃣ Communication Methods**: 
- **Synchronous**: REST API (HTTP/JSON) - for queries and immediate operations
- **Asynchronous**: Event-Driven (RabbitMQ) - for notifications and decoupling

#### **3️⃣ Data Strategy**: Polyglot Persistence
- **MySQL**: Transactional data (Auth, Order, Payment)
- **MongoDB**: Flexible schema data (User, Review, Notification)

#### **4️⃣ Cloud Platform**: 
- **AWS RDS**: MySQL managed service (Multi-AZ high availability)
- **MongoDB Atlas**: MongoDB cloud service (Replica Set)
- **AWS EC2/ECS**: Application servers (optional Kubernetes)

#### **5️⃣ High Availability Design**:
- **MySQL**: Multi-AZ dual availability zone, automatic failover
- **MongoDB**: 3-node Replica Set, automatic master-slave switching
- **RabbitMQ**: Message persistence (durable=True)
- **Services**: Stateless design, horizontally scalable (add more instances)

#### **6️⃣ Caching Strategy**:
- **Redis**: Unified cache layer
  - Rate Limiting (rate limit counters)
  - Session Cache
  - Notification Cache

---

### Key Design Decisions

#### **1️⃣ API Gateway Pattern**
**Decision**: Use single gateway as unified entry point  
**Advantages**:
- ✅ Simplify client calls (only need to know one address)
- ✅ Centralized authentication and authorization (JWT verification handled uniformly)
- ✅ Traffic control and rate limiting (prevent malicious attacks)
- ✅ Service discovery and routing (clients don't need to know service addresses)

**Code Implementation**:
```python
# gateway-service/src/gateway_service/api/routes.py
@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(path: str, request: Request):
    # 1. JWT verification
    # 2. Rate limit check
    # 3. Route to corresponding service
```

---

#### **2️⃣ Database per Service**
**Decision**: Each microservice owns independent database  
**Advantages**:
- ✅ Avoid coupling between services (changing one service's tables doesn't affect others)
- ✅ Independent scaling (Order service can upgrade database performance alone)
- ✅ Fault isolation (Auth DB down doesn't affect Review service)

**Implementation**:
- Auth Service → `auth_db` (MySQL)
- User Service → `user_db` (MongoDB)
- Order Service → `order_db` (MySQL)
- Payment Service → `payment_db` (MySQL)
- Review Service → `review_db` (MongoDB)
- Notification Service → `notification_db` (MongoDB)

---

#### **3️⃣ Event-Driven Architecture**
**Decision**: Use RabbitMQ for asynchronous service communication  
**Advantages**:
- ✅ Decouple service dependencies (Order Service doesn't need Notification Service address)
- ✅ Asynchronous processing (return immediately after order publish, notification sent asynchronously)
- ✅ Scalability (add new Consumer without modifying Producer)
- ✅ Fault tolerance (message queue buffers, Consumer temporarily down doesn't lose messages)

**Actual Scenario**:
```
Order creation flow:
1. Order Service → MySQL (save order)
2. Order Service → RabbitMQ (publish order.created event)
3. RabbitMQ → Notification Service (asynchronous consumption)
4. Notification Service → MongoDB (insert notification)
5. Notification Service → Email/SMS (send email/SMS)
```

---

#### **4️⃣ Polyglot Persistence**
**Decision**: Choose different databases based on data characteristics  
**MySQL Use Cases**:
- **Auth Service**: User authentication needs ACID transactions (lock account on wrong password)
- **Order Service**: Order status transitions need strong consistency (no phantom reads)
- **Payment Service**: Financial transactions must be precise (DECIMAL type + transactions)

**MongoDB Use Cases**:
- **User Service**: User profiles flexible extension (Provider skill list length unfixed)
- **Review Service**: Review content unstructured (full-text search requirement)
- **Notification Service**: High concurrent writes (tens of thousands notifications daily)

---

#### **5️⃣ Stateless Services**
**Decision**: All microservices don't save session state  
**Advantages**:
- ✅ Horizontal scaling (can add more service instances anytime)
- ✅ Load balancing (any instance can handle requests)
- ✅ Strong fault tolerance (single instance down doesn't affect user sessions)

**Implementation Method**:
- JWT Token stores user information (no server-side Session needed)
- Redis stores shared state (rate limit counters, blacklist)

---

#### **6️⃣ Centralized Cache**
**Decision**: Use Redis as unified cache layer  
**Advantages**:
- ✅ Performance improvement (hot data cache, reduce DB queries)
- ✅ Rate limiting protection (Redis counter-based implementation)
- ✅ Cross-service sharing (multiple services share one Redis)

**Use Cases**:
```python
# Rate limiting example
key = f"rate_limit:{user_id}"
count = await redis.incr(key)
if count == 1:
    await redis.expire(key, 60)
if count > 100:
    raise HTTPException(429, "Too Many Requests")
```

---

### Actual Deployment Scripts

#### **Local Development Environment Startup**:
```bash
# 1. Start infrastructure
cd infrastructure
docker-compose up -d mysql mongodb rabbitmq redis

# 2. Start all services
cd ..
./scripts/start-services.sh

# Includes following commands:
# - uvicorn auth_service.main:app --port 8000 --app-dir src &
# - uvicorn user_service.main:app --port 8002 --app-dir src &
# - uvicorn order_service.main:app --port 8003 --app-dir src &
# - uvicorn payment_service.main:app --port 8004 --app-dir src &
# - uvicorn review_service.main:app --port 8005 --app-dir src &
# - uvicorn notification_service.main:app --port 8006 --app-dir src &
# - uvicorn gateway_service.main:app --port 8080 --app-dir src &

# 3. Start frontend
cd frontend
npm run dev  # Development environment
# or
npm run build && nginx  # Production environment
```

#### **Kubernetes Deployment Example**:
```bash
# 1. Deploy MySQL StatefulSet
kubectl apply -f infrastructure/kubernetes/mysql/

# 2. Deploy MongoDB StatefulSet
kubectl apply -f infrastructure/kubernetes/mongodb/

# 3. Deploy RabbitMQ
kubectl apply -f infrastructure/kubernetes/rabbitmq/

# 4. Deploy Redis
kubectl apply -f infrastructure/kubernetes/redis/

# 5. Deploy microservices
kubectl apply -f infrastructure/kubernetes/auth-service/
kubectl apply -f infrastructure/kubernetes/user-service/
kubectl apply -f infrastructure/kubernetes/order-service/
kubectl apply -f infrastructure/kubernetes/payment-service/
kubectl apply -f infrastructure/kubernetes/review-service/
kubectl apply -f infrastructure/kubernetes/notification-service/
kubectl apply -f infrastructure/kubernetes/gateway-service/
```

---

### Presentation Tips (Deployment Diagram Explanation)

**Explanation Order**:
1. **Outside to Inside**: Internet → AWS Cloud → Services → Databases
2. **Top to Bottom**: Client → Frontend → Gateway → Microservices → Infrastructure → Databases
3. **Layer by Layer**: First explain 5 major layers, then dive into each layer's details

**Key Demonstration Points**:
- **UML Stereotypes**: Explain meaning of `<<location>>`, `<<artifact>>`, `<<database>>` symbols
- **Communication Patterns**: 
  - Solid arrows (synchronous HTTP)
  - Dashed arrows (deployment relationships/cache)
  - Bold arrows (asynchronous messages)
- **High Availability Design**: 
  - MySQL Multi-AZ automatic failover
  - MongoDB 3-node Replica Set
  - Microservices stateless, horizontally scalable
- **Database Selection**: 
  - MySQL for transactions (Auth, Order, Payment)
  - MongoDB for flexible schema (User, Review, Notification)

**Code Demo**:
```bash
# Demo local startup of all services
./scripts/start-services.sh

# Demo viewing running status
ps aux | grep uvicorn
netstat -an | grep LISTEN | grep -E '800[0-6]|8080'

# Demo accessing services
curl http://localhost:8080/health  # Gateway health check
curl http://localhost:8000/health  # Auth Service health check
```

**Possible Questions**:

**Q1: Why need API Gateway, can't frontend directly call each service?**  
A: 
- ❌ Without Gateway: Frontend needs to know 7 service addresses, each request must add JWT Header manually
- ✅ With Gateway: Frontend only needs one address (8080), Gateway handles authentication and routing uniformly
- Additionally, Gateway provides rate limiting protection against malicious attacks

**Q2: 6 microservices with 6 databases, isn't it too complex?**  
A:
- This is **Database per Service** pattern, microservices architecture best practice
- Advantage: Each service can independently choose most suitable database (MySQL vs MongoDB)
- Advantage: Changing one service's table structure doesn't affect other services
- Disadvantage: Cannot use cross-database JOIN, need API calls or events

**Q3: If Order Service needs User information but they're in different databases, how to query?**  
A:
- **Method 1 (Recommended)**: Order Service calls User Service API via HTTP
  ```python
  user_data = await http_client.get(f"http://user-service:8002/users/{user_id}")
  ```
- **Method 2**: Order Service subscribes to User Service events, maintains local cache
- **Method 3**: Use API Gateway to aggregate multiple service data (BFF pattern)

**Q4: RabbitMQ and Redis are both middleware, why need both?**  
A:
- **RabbitMQ**: Message queue for **asynchronous event communication** (decouple service dependencies)
  - Example: After Order created, asynchronously notify Notification Service to send email
- **Redis**: In-memory cache for **performance optimization and rate limiting**
  - Example: Cache user permissions, rate limit counters, hot data
- Different responsibilities, cannot replace each other

**Q5: If deploying to Kubernetes, need to change code?**  
A:
- **No code changes needed** (FastAPI applications are container-friendly)
- **Only need to add**:
  1. Dockerfile (one per service)
  2. Kubernetes YAML (Deployment + Service + ConfigMap)
  3. Ingress configuration (replaces some API Gateway functions)
- This project already provides K8s config: `infrastructure/kubernetes/`

**Q6: Why use AWS RDS for MySQL and Atlas for MongoDB instead of self-hosting?**  
A:
- **Managed Service Advantages**:
  - ✅ Automatic backup (AWS RDS daily backup, 7-day retention)
  - ✅ Automatic failover (Multi-AZ, switch within seconds)
  - ✅ Automatic scaling (storage auto-expands when insufficient)
  - ✅ Monitoring and alerting (CloudWatch integration)
- **Self-hosted Database Disadvantages**:
  - ❌ Need to write backup scripts yourself
  - ❌ Need to monitor disk space yourself
  - ❌ Need manual master-slave switching during downtime
- **Cost Comparison**: For production, managed services are actually cheaper (considering operational labor costs)

---

### Relationship with Other Architecture Diagrams

| Diagram | Connection Point | Description |
|---------|-----------------|-------------|
| **Diagram 1: Logical Architecture** | Physical mapping of logical architecture | Logical Architecture shows 5-layer logical structure, Deployment Diagram shows how these 5 layers deploy in actual environment |
| **Diagram 2: DDD Diagram** | Physical embodiment of service boundaries | Each Bounded Context (service) in DDD corresponds to one Artifact (JAR package) in Deployment |
| **Diagram 3: Event-Driven** | RabbitMQ physical deployment | Exchange and Queue in Event-Driven diagram embodied as RabbitMQ node in Deployment |
| **Diagram 4: Polyglot Persistence** | Database physical location | MySQL/MongoDB in Polyglot diagram shown as AWS RDS and MongoDB Atlas in Deployment |
| **Diagram 5/6: Sequence Diagrams** | Physical path of interaction flow | Service calls in Sequence correspond to solid arrows (HTTP) and bold arrows (Events) in Deployment |

**Comprehensive Explanation Suggestion**:
1. **First explain Diagram 1 (Logical Architecture)**: Establish logical layer concept
2. **Then explain Diagram 7 (Deployment Diagram)**: Show how logic maps to physical
3. **Compare both diagrams**: Emphasize "logical architecture design → physical deployment implementation" evolution process

---

**Document Version**: v4.0  
**Last Updated**: 2025-10-25  
**Applicable Scenarios**: Technical sharing, Architecture review, New employee training, Pre demonstration  
**Included Diagrams**: 7 (Logical Architecture, DDD, Event-Driven, Polyglot Persistence, Customer Publish Order Sequence, Provider Accept Order Sequence, Logical Detail Deployment)
