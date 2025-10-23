# Notification Service Postman 测试指南

## 📋 测试前准备

### ✅ 确认所有服务已启动
```bash
# 检查服务状态
lsof -i :8000  # Auth Service
lsof -i :8002  # User Service
lsof -i :8003  # Order Service
lsof -i :8004  # Payment Service
lsof -i :8005  # Review Service
lsof -i :8006  # Notification Service ⭐

# 检查基础设施
lsof -i :27017  # MongoDB
lsof -i :6379   # Redis
lsof -i :5672   # RabbitMQ
```

### 📌 Notification Service 端点总览

**Customer 端点（需要认证）**
- `GET /customer/inbox/` - 获取客户收件箱

**Provider 端点（需要认证）**
- `GET /provider/inbox/` - 获取服务商收件箱

**系统端点**
- `GET /health` - 健康检查

---

## 🎯 Notification Service 工作原理

### 事件驱动架构
Notification Service 是一个**被动服务**，它通过监听 RabbitMQ 事件来触发通知：

1. **订单事件** (Order Service)
   - `order.created` → 通知 Customer：订单创建成功
   - `order.accepted` → 通知 Customer 和 Provider：订单被接受
   - `order.cancelled` → 通知相关方：订单取消

2. **支付事件** (Payment Service)
   - `payment.completed` → 通知 Customer 和 Provider：支付成功
   - `payment.failed` → 通知 Customer：支付失败

3. **评价事件** (Review Service)
   - `review.created` → 通知 Customer 和 Provider：评价创建成功

### 通知存储
- **MongoDB**: 存储通知历史记录
  - `customer_inbox` 集合：客户收件箱
  - `provider_inbox` 集合：服务商收件箱
- **Redis**: 可用于实时推送（未来功能）

---

## 🧪 完整测试流程

### 步骤 0: 健康检查

**请求**
```
GET http://localhost:8006/health
```

**预期响应 200**
```json
{
  "status": "healthy",
  "service": "notification-service",
  "version": "1.0.0"
}
```

---

### 步骤 1: 准备测试用户

#### 1.1 注册并登录 Customer

**注册**
```
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "username": "customer_notif",
  "email": "customer_notif@test.com",
  "password": "Test123456",
  "role": "customer"
}
```

**登录**
```
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "username": "customer_notif",
  "password": "Test123456"
}
```

📌 **保存 customer_token** = `<customer的access_token>`

#### 1.2 注册并登录 Provider

**注册**
```
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "username": "provider_notif",
  "email": "provider_notif@test.com",
  "password": "Test123456",
  "role": "provider"
}
```

**登录**
```
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "username": "provider_notif",
  "password": "Test123456"
}
```

📌 **保存 provider_token** = `<provider的access_token>`

---

### 步骤 2: 创建 Profiles

**创建 Customer Profile**
```
POST http://localhost:8002/customer/profile/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "location": "NORTH",
  "address": "123 Test St",
  "budget_preference": 1000
}
```

**创建 Provider Profile**
```
POST http://localhost:8002/provider/profile/
Authorization: Bearer <provider_token>
Content-Type: application/json

{
  "location": "NORTH",
  "service_type": "cleaning",
  "service_description": "Professional cleaning service",
  "price_per_hour": 50.0
}
```

---

### 步骤 3: 触发订单创建通知 ⭐

#### 3.1 Customer 创建订单

**请求**
```
POST http://localhost:8003/customer/orders/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "title": "Need cleaning service",
  "description": "Clean my house",
  "service_type": "cleaning",
  "price": 100.0,
  "location": "NORTH"
}
```

**预期响应**
```json
{
  "order_id": 1,
  "status": "pending",
  "message": "Order published successfully."
}
```

📌 **保存 order_id** = `1`

#### 3.2 验证 Customer 收到通知

**请求**
```
GET http://localhost:8006/customer/inbox/
Authorization: Bearer <customer_token>
```

**预期响应 200**
```json
{
  "items": [
    {
      "customer_id": 1,
      "order_id": 1,
      "message": "You have successfully published the order: 1.",
      "created_at": "2025-10-16T12:00:00",
      "is_read": false
    }
  ],
  "total": 1
}
```

**验证点**
- ✅ Customer 收到 1 条通知
- ✅ 通知内容包含订单 ID
- ✅ `is_read` 为 `false`

---

### 步骤 4: 触发订单接受通知 ⭐

#### 4.1 Provider 接受订单

**请求**
```
PUT http://localhost:8003/provider/orders/1/accept
Authorization: Bearer <provider_token>
Content-Type: application/json
```

**预期响应**
```json
{
  "order_id": 1,
  "status": "accepted",
  "message": "Order accepted successfully."
}
```

#### 4.2 验证 Customer 收到通知

**请求**
```
GET http://localhost:8006/customer/inbox/
Authorization: Bearer <customer_token>
```

**预期响应 200**
```json
{
  "items": [
    {
      "customer_id": 1,
      "order_id": 1,
      "message": "Your order: 1 has been accepted by provider: 2.",
      "created_at": "2025-10-16T12:01:00",
      "is_read": false
    },
    {
      "customer_id": 1,
      "order_id": 1,
      "message": "You have successfully published the order: 1.",
      "created_at": "2025-10-16T12:00:00",
      "is_read": false
    }
  ],
  "total": 2
}
```

**验证点**
- ✅ Customer 现在有 2 条通知（最新的在前）
- ✅ 新通知提到订单被接受

#### 4.3 验证 Provider 收到通知

**请求**
```
GET http://localhost:8006/provider/inbox/
Authorization: Bearer <provider_token>
```

**预期响应 200**
```json
{
  "items": [
    {
      "provider_id": 2,
      "order_id": 1,
      "message": "You have successfully accepted the order: 1.",
      "created_at": "2025-10-16T12:01:00",
      "is_read": false
    }
  ],
  "total": 1
}
```

**验证点**
- ✅ Provider 收到 1 条通知
- ✅ 通知内容确认订单被接受

---

### 步骤 5: 触发支付完成通知 ⭐

#### 5.1 Customer 充值余额

**请求**
```
POST http://localhost:8004/customer/payments/recharge
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "amount": 500
}
```

#### 5.2 Provider 完成订单

**请求**
```
PUT http://localhost:8003/provider/orders/1/complete
Authorization: Bearer <provider_token>
Content-Type: application/json
```

#### 5.3 Customer 支付订单

**请求**
```
POST http://localhost:8004/customer/payments/pay
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "order_id": 1
}
```

**预期响应**
```json
{
  "transaction_id": 1,
  "order_id": 1,
  "amount": 100.0,
  "status": "completed",
  "message": "Payment successful."
}
```

#### 5.4 验证 Customer 收到支付通知

**请求**
```
GET http://localhost:8006/customer/inbox/
Authorization: Bearer <customer_token>
```

**预期响应 200**
```json
{
  "items": [
    {
      "customer_id": 1,
      "order_id": 1,
      "message": "Payment for order 1 completed successfully.",
      "created_at": "2025-10-16T12:05:00",
      "is_read": false
    },
    // ... 之前的通知
  ],
  "total": 3
}
```

**验证点**
- ✅ Customer 现在有 3 条通知
- ✅ 最新通知是支付成功

#### 5.5 验证 Provider 收到支付通知

**请求**
```
GET http://localhost:8006/provider/inbox/
Authorization: Bearer <provider_token>
```

**预期响应 200**
```json
{
  "items": [
    {
      "provider_id": 2,
      "order_id": 1,
      "message": "Payment for order 1 received.",
      "created_at": "2025-10-16T12:05:00",
      "is_read": false
    },
    {
      "provider_id": 2,
      "order_id": 1,
      "message": "You have successfully accepted the order: 1.",
      "created_at": "2025-10-16T12:01:00",
      "is_read": false
    }
  ],
  "total": 2
}
```

**验证点**
- ✅ Provider 现在有 2 条通知
- ✅ 最新通知是收到付款

---

### 步骤 6: 触发评价创建通知 ⭐

#### 6.1 Customer 创建评价

**请求**
```
POST http://localhost:8005/reviews/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "order_id": 1,
  "stars": 5,
  "content": "Excellent service!"
}
```

**预期响应**
```json
{
  "review_id": "1",
  "order_id": 1,
  "stars": 5,
  "content": "Excellent service!",
  "message": "Review created successfully."
}
```

#### 6.2 验证 Customer 收到评价通知

**请求**
```
GET http://localhost:8006/customer/inbox/
Authorization: Bearer <customer_token>
```

**预期响应 200**
```json
{
  "items": [
    {
      "customer_id": 1,
      "order_id": 1,
      "message": "You have successfully reviewed order 1.",
      "created_at": "2025-10-16T12:10:00",
      "is_read": false
    },
    // ... 之前的通知
  ],
  "total": 4
}
```

**验证点**
- ✅ Customer 现在有 4 条通知
- ✅ 最新通知确认评价创建成功

#### 6.3 验证 Provider 收到评价通知

**请求**
```
GET http://localhost:8006/provider/inbox/
Authorization: Bearer <provider_token>
```

**预期响应 200**
```json
{
  "items": [
    {
      "provider_id": 2,
      "order_id": 1,
      "message": "Customer has reviewed your order 1 with 5 stars.",
      "created_at": "2025-10-16T12:10:00",
      "is_read": false
    },
    // ... 之前的通知
  ],
  "total": 3
}
```

**验证点**
- ✅ Provider 现在有 3 条通知
- ✅ 最新通知包含评价星级（5 stars）

---

## 🧪 边界情况测试

### 测试 7: 未认证访问（应失败）

**测试 Customer 端点**
```
GET http://localhost:8006/customer/inbox/
```

**预期响应 403**
```json
{
  "detail": "Not authenticated"
}
```

**测试 Provider 端点**
```
GET http://localhost:8006/provider/inbox/
```

**预期响应 403**
```json
{
  "detail": "Not authenticated"
}
```

---

### 测试 8: 使用错误角色的 Token（应失败）

**场景**: Customer 使用自己的 token 访问 Provider 端点

**请求**
```
GET http://localhost:8006/provider/inbox/
Authorization: Bearer <customer_token>
```

**预期行为**
- ✅ 返回 200，但是收件箱为空（因为该 customer_id 没有对应的 provider 通知）
- ✅ 或者根据业务逻辑，可能返回空列表

```json
{
  "items": [],
  "total": 0
}
```

---

### 测试 9: 验证通知按时间倒序排列

**请求**
```
GET http://localhost:8006/customer/inbox/
Authorization: Bearer <customer_token>
```

**验证点**
- ✅ 最新的通知在最前面
- ✅ `created_at` 时间戳递减
- ✅ 最多返回 100 条通知（DAO 中的限制）

---

### 测试 10: 多订单场景

#### 10.1 创建第二个订单

**请求**
```
POST http://localhost:8003/customer/orders/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "title": "Second cleaning job",
  "description": "Clean kitchen",
  "service_type": "cleaning",
  "price": 80.0,
  "location": "NORTH"
}
```

#### 10.2 验证通知包含不同订单

**请求**
```
GET http://localhost:8006/customer/inbox/
Authorization: Bearer <customer_token>
```

**验证点**
- ✅ 通知列表包含多个订单的通知
- ✅ 每条通知的 `order_id` 正确对应
- ✅ 通知总数增加

---

## 🔄 完整业务流程测试总结

### 一个订单的完整生命周期通知

| 步骤 | 操作 | Customer 通知 | Provider 通知 |
|------|------|---------------|---------------|
| 1 | Customer 创建订单 | ✅ "订单创建成功" | - |
| 2 | Provider 接受订单 | ✅ "订单被接受" | ✅ "成功接受订单" |
| 3 | Provider 完成订单 | - | - |
| 4 | Customer 支付订单 | ✅ "支付成功" | ✅ "收到付款" |
| 5 | Customer 创建评价 | ✅ "评价创建成功" | ✅ "收到 5 星评价" |

**预期结果**
- Customer 收件箱：**4 条通知**
- Provider 收件箱：**3 条通知**

---

## ✅ 完整测试检查清单

### 基础功能
- [ ] 健康检查返回 200
- [ ] Customer 可以获取自己的收件箱
- [ ] Provider 可以获取自己的收件箱
- [ ] 通知按时间倒序排列

### 事件触发 - 订单事件
- [ ] 订单创建 → Customer 收到通知
- [ ] 订单接受 → Customer 和 Provider 都收到通知
- [ ] Provider 接受通知内容包含正确的订单 ID

### 事件触发 - 支付事件
- [ ] 支付成功 → Customer 和 Provider 都收到通知
- [ ] Customer 通知提示"支付成功"
- [ ] Provider 通知提示"收到付款"

### 事件触发 - 评价事件
- [ ] 评价创建 → Customer 和 Provider 都收到通知
- [ ] Customer 通知确认评价创建
- [ ] Provider 通知包含评分星级

### 权限验证
- [ ] 未认证请求返回 403
- [ ] Customer token 只能访问 customer inbox
- [ ] Provider token 只能访问 provider inbox

### 数据完整性
- [ ] 通知包含正确的 user_id
- [ ] 通知包含正确的 order_id
- [ ] 通知消息内容准确
- [ ] `is_read` 字段默认为 false
- [ ] `created_at` 时间戳正确

---

## 🔍 验证数据库数据

### 查看 MongoDB 数据

```javascript
// 连接到 MongoDB
use notification_db

// 查看客户收件箱
db.customer_inbox.find().pretty()

// 查看服务商收件箱
db.provider_inbox.find().pretty()

// 统计通知数量
db.customer_inbox.countDocuments()
db.provider_inbox.countDocuments()

// 查看特定客户的通知
db.customer_inbox.find({ customer_id: 1 }).sort({ created_at: -1 })

// 查看特定服务商的通知
db.provider_inbox.find({ provider_id: 2 }).sort({ created_at: -1 })
```

**预期数据结构**

**customer_inbox 集合**
```json
{
  "customer_id": 1,
  "order_id": 1,
  "message": "Payment for order 1 completed successfully.",
  "created_at": ISODate("2025-10-16T12:05:00.000Z"),
  "is_read": false
}
```

**provider_inbox 集合**
```json
{
  "provider_id": 2,
  "order_id": 1,
  "message": "Payment for order 1 received.",
  "created_at": ISODate("2025-10-16T12:05:00.000Z"),
  "is_read": false
}
```

---

## 🔍 验证 RabbitMQ 消息队列

### 检查 RabbitMQ 管理界面

访问：http://localhost:15672
- 用户名：guest
- 密码：guest

**检查项目**
1. **Exchanges** 页面
   - ✅ `order_events` exchange 存在
   - ✅ `payment_events` exchange 存在
   - ✅ `review_events` exchange 存在
   - ✅ `notification_events` exchange 存在

2. **Queues** 页面
   - ✅ Notification Service 的临时队列存在
   - ✅ 队列绑定到正确的 routing keys

3. **Messages** 计数
   - 查看每个事件的消息发布数量
   - 确认消息被正确消费（队列为空）

---

## 📊 Postman Collection 示例

### Environment Variables
```json
{
  "auth_url": "http://localhost:8000",
  "user_url": "http://localhost:8002",
  "order_url": "http://localhost:8003",
  "payment_url": "http://localhost:8004",
  "review_url": "http://localhost:8005",
  "notification_url": "http://localhost:8006",
  "customer_token": "<set_after_login>",
  "provider_token": "<set_after_login>",
  "order_id": "<set_after_creating_order>"
}
```

### 使用变量的请求示例

**获取客户收件箱**
```
GET {{notification_url}}/customer/inbox/
Authorization: Bearer {{customer_token}}
```

**获取服务商收件箱**
```
GET {{notification_url}}/provider/inbox/
Authorization: Bearer {{provider_token}}
```

---

## 🐛 常见错误排查

### 错误 1: 收件箱为空，但应该有通知

**可能原因**
1. RabbitMQ 未启动或连接失败
2. Notification Service 的事件消费者未启动
3. 其他服务的事件发布失败

**排查步骤**
```bash
# 1. 检查 RabbitMQ 是否运行
lsof -i :5672

# 2. 检查 Notification Service 日志
# 查看终端输出，应该看到：
# ✅ Connected to MongoDB
# ✅ Connected to Redis
# ✅ Connected to RabbitMQ

# 3. 检查其他服务是否成功发布事件
# 查看 Order/Payment/Review Service 日志
```

**解决方案**
```bash
# 重启 RabbitMQ
brew services restart rabbitmq

# 重启 Notification Service
cd services/notification-service
uvicorn notification_service.main:app --reload --host 0.0.0.0 --port 8006 --app-dir src
```

---

### 错误 2: 401 Unauthorized

**原因**: Token 无效或未提供

**解决**
- 重新登录获取新 token
- 检查 Authorization header 格式: `Bearer <token>`

---

### 错误 3: 503 Service Unavailable - Auth service unavailable

**原因**: Auth Service 未启动或连接失败

**解决**
```bash
# 检查 Auth Service
lsof -i :8000

# 重启 Auth Service
cd services/auth-service
uvicorn auth_service.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

---

### 错误 4: 通知延迟或缺失

**可能原因**
1. RabbitMQ 消息未被消费
2. MongoDB 写入失败
3. 事件处理器抛出异常

**排查步骤**
```bash
# 1. 查看 RabbitMQ 管理界面
# 检查队列中是否有积压的消息

# 2. 查看 Notification Service 日志
# 查找错误或异常信息

# 3. 手动查询 MongoDB
mongo
use notification_db
db.customer_inbox.find().pretty()
db.provider_inbox.find().pretty()
```

---

## 💡 测试技巧

### 1. 使用 Postman Tests 自动验证

在 Postman 的 Tests 标签页添加：

```javascript
// 验证 Customer 收件箱
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has items array", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.items).to.be.an('array');
});

pm.test("Total count matches items length", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.total).to.equal(jsonData.items.length);
});

pm.test("Notifications are sorted by created_at desc", function () {
    const jsonData = pm.response.json();
    const items = jsonData.items;
    for (let i = 0; i < items.length - 1; i++) {
        const current = new Date(items[i].created_at);
        const next = new Date(items[i + 1].created_at);
        pm.expect(current >= next).to.be.true;
    }
});
```

---

### 2. 创建端到端测试流程

在 Postman Collection 中创建一个文件夹 "End-to-End Notification Test"，包含：

1. **Setup** 文件夹
   - Register Customer
   - Login Customer
   - Register Provider
   - Login Provider
   - Create Profiles

2. **Order Flow** 文件夹
   - Create Order
   - Check Customer Inbox (expect 1 notification)
   - Accept Order
   - Check Customer Inbox (expect 2 notifications)
   - Check Provider Inbox (expect 1 notification)

3. **Payment Flow** 文件夹
   - Recharge Balance
   - Complete Order
   - Pay Order
   - Check Customer Inbox (expect 3 notifications)
   - Check Provider Inbox (expect 2 notifications)

4. **Review Flow** 文件夹
   - Create Review
   - Check Customer Inbox (expect 4 notifications)
   - Check Provider Inbox (expect 3 notifications)

使用 Postman Collection Runner 按顺序执行所有请求。

---

### 3. 等待事件处理

由于通知是异步处理的，建议在触发事件后等待 1-2 秒再查询收件箱：

```javascript
// 在 Postman Tests 中添加延迟
setTimeout(function(){}, 2000);
```

或者手动等待几秒后再发送下一个请求。

---

## 🎯 测试完成标准

全部测试通过条件：

### 功能测试
✅ 健康检查正常
✅ Customer 和 Provider 都能获取各自的收件箱
✅ 通知按时间倒序排列
✅ 最多返回 100 条通知

### 事件测试
✅ 订单创建事件 → 1 条 Customer 通知
✅ 订单接受事件 → 1 条 Customer 通知 + 1 条 Provider 通知
✅ 支付完成事件 → 1 条 Customer 通知 + 1 条 Provider 通知
✅ 评价创建事件 → 1 条 Customer 通知 + 1 条 Provider 通知

### 数据完整性
✅ MongoDB 有对应的通知记录
✅ 通知内容准确（订单 ID、消息文本）
✅ `is_read` 默认为 `false`
✅ `created_at` 时间戳正确

### 权限测试
✅ 未认证请求返回 403
✅ 只能访问自己的收件箱

### 完整流程
✅ 一个订单从创建到评价，Customer 收到 4 条通知
✅ 一个订单从创建到评价，Provider 收到 3 条通知

**Notification Service 测试完成！🎉**
