# Review Service Postman 测试指南

## 📋 测试前准备

### ✅ 确认所有服务已启动
```bash
# 检查服务状态
lsof -i :8000  # Auth Service
lsof -i :8002  # User Service  
lsof -i :8003  # Order Service
lsof -i :8004  # Payment Service
lsof -i :8005  # Review Service ⭐
```

### 📌 Review Service 端点总览

**Customer 端点**
- `POST /reviews/` - 创建评价（需要认证）

**Provider 专用端点（需要认证）**
- `GET /reviews/provider/me/rating` - 获取当前 Provider 的评分
- `GET /reviews/provider/me/reviews` - 获取当前 Provider 的所有评价

**公开查询端点**
- `GET /reviews/provider/{provider_id}/rating` - 获取指定服务商评分
- `GET /reviews/provider/{provider_id}` - 获取指定服务商所有评价
- `GET /reviews/order/{order_id}` - 获取订单评价

**系统端点**
- `GET /health` - 健康检查

---

## 🧪 完整测试流程

### 步骤 0: 健康检查

**请求**
```
GET http://localhost:8005/health
```

**预期响应 200**
```json
{
  "status": "healthy",
  "service": "review-service",
  "version": "1.0.0"
}
```

---

### 步骤 1: 准备测试数据

#### 1.1 注册并登录 Customer

**注册 Customer**
```
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "username": "customer_review",
  "email": "customer_review@test.com",
  "password": "Test123456",
  "role": "customer"
}
```

**登录获取 Token**
```
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "username": "customer_review",
  "password": "Test123456"
}
```

**响应示例**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

📌 **保存 customer_token** = `<customer的access_token>`

#### 1.2 注册并登录 Provider

**注册 Provider**
```
POST http://localhost:8000/auth/register
Content-Type: application/json

{
  "username": "provider_review",
  "email": "provider_review@test.com",
  "password": "Test123456",
  "role": "provider"
}
```

**登录获取 Token**
```
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "username": "provider_review",
  "password": "Test123456"
}
```

📌 **保存 provider_token** = `<provider的access_token>`

#### 1.3 创建 Profiles

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

#### 1.4 充值余额

```
POST http://localhost:8004/customer/payments/recharge
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "amount": 500
}
```

#### 1.5 创建并完成订单

**Customer 创建订单**
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

**响应示例**
```json
{
  "order_id": 1,
  "title": "Need cleaning service",
  ...
}
```

📌 **保存 order_id** = `1`

**Provider 接受订单**
```
PUT http://localhost:8003/provider/orders/1/accept
Authorization: Bearer <provider_token>
Content-Type: application/json
```

**Provider 完成订单**
```
PUT http://localhost:8003/provider/orders/1/complete
Authorization: Bearer <provider_token>
Content-Type: application/json
```

**Customer 支付订单**
```
POST http://localhost:8004/customer/payments/pay
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "order_id": 1
}
```

---

### 步骤 2: 测试创建评价 ⭐

**请求**
```
POST http://localhost:8005/reviews/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "order_id": 1,
  "stars": 5,
  "content": "Excellent service! Very professional and thorough."
}
```

**说明**
- ✅ 不需要传递 `customer_id` 和 `provider_id`
- ✅ 系统会从 Order Service 自动获取订单信息
- ✅ 自动验证订单属于当前用户
- ✅ 自动验证订单已完成且已支付

**预期响应 201**
```json
{
  "review_id": "1",
  "order_id": 1,
  "stars": 5,
  "content": "Excellent service! Very professional and thorough.",
  "message": "Review created successfully."
}
```

**验证结果**
- ✅ MongoDB `review_db.reviews` 集合有新文档
- ✅ MongoDB `review_db.provider_ratings` 集合有 provider 评分记录
- ✅ RabbitMQ 发布了 `review.created` 事件
- ✅ RabbitMQ 发布了 `rating.updated` 事件

---

### 步骤 3: 测试获取服务商评分（公开接口）

**请求**
```
GET http://localhost:8005/reviews/provider/<provider_user_id>/rating
```

**预期响应 200**
```json
{
  "provider_id": 2,
  "average_rating": 5.0,
  "total_reviews": 1
}
```

---

### 步骤 3.1: Provider 查看自己的评分 ⭐

**请求**
```
GET http://localhost:8005/reviews/provider/me/rating
Authorization: Bearer <provider_token>
```

**说明**
- ✅ Provider 不需要知道自己的 user_id
- ✅ 直接使用 token 即可查看自己的评分
- ✅ 自动从 token 中提取 provider_id

**预期响应 200**
```json
{
  "provider_id": 2,
  "average_rating": 5.0,
  "total_reviews": 1
}
```

---

### 步骤 4: 测试获取服务商所有评价（公开接口）

**请求**
```
GET http://localhost:8005/reviews/provider/<provider_user_id>
```

**预期响应 200**
```json
[
  {
    "order_id": 1,
    "customer_id": 1,
    "stars": 5,
    "content": "Excellent service! Very professional and thorough.",
    "created_at": "2025-10-16T12:00:00Z"
  }
]
```

---

### 步骤 4.1: Provider 查看自己的所有评价 ⭐

**请求**
```
GET http://localhost:8005/reviews/provider/me/reviews
Authorization: Bearer <provider_token>
```

**说明**
- ✅ Provider 不需要知道自己的 user_id
- ✅ 直接使用 token 即可查看自己的所有评价
- ✅ 自动从 token 中提取 provider_id

**预期响应 200**
```json
[
  {
    "order_id": 1,
    "customer_id": 1,
    "stars": 5,
    "content": "Excellent service! Very professional and thorough.",
    "created_at": "2025-10-16T12:00:00Z"
  }
]
```

---

### 步骤 5: 测试根据订单获取评价

**请求**
```
GET http://localhost:8005/reviews/order/1
```

**预期响应 200**
```json
{
  "order_id": 1,
  "customer_id": 1,
  "provider_id": 2,
  "stars": 5,
  "content": "Excellent service! Very professional and thorough.",
  "created_at": "2025-10-16T12:00:00Z"
}
```

---

## 🧪 边界情况测试

### 测试 6: 重复评价同一订单（应失败）

**请求**
```
POST http://localhost:8005/reviews/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "order_id": 1,
  "stars": 4,
  "content": "Trying to review again"
}
```

**预期响应 400**
```json
{
  "detail": "This order has already been reviewed"
}
```

---

### 测试 7: 评价他人订单（应失败）

**场景**: 使用 provider token 尝试评价 customer 的订单

**请求**
```
POST http://localhost:8005/reviews/
Authorization: Bearer <provider_token>  ⚠️ 使用 provider token
Content-Type: application/json

{
  "order_id": 1,  ⚠️ 这是 customer 的订单
  "stars": 5,
  "content": "Fake review"
}
```

**预期响应 403**
```json
{
  "detail": "You can only review your own orders"
}
```

---

### 测试 8: 未认证访问（应失败）

**请求**
```
POST http://localhost:8005/reviews/
Content-Type: application/json

{
  "order_id": 1,
  "stars": 5,
  "content": "No auth"
}
```

**预期响应 401**
```json
{
  "detail": "Not authenticated"
}
```

---

### 测试 9: 评分超出范围（应失败）

**请求**
```
POST http://localhost:8005/reviews/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "order_id": 2,
  "stars": 6,  ⚠️ 超出范围（1-5）
  "content": "Invalid stars"
}
```

**预期响应 422**
```json
{
  "detail": [
    {
      "loc": ["body", "stars"],
      "msg": "ensure this value is less than or equal to 5",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

### 测试 10: 评价未完成的订单（应失败）

**场景**: 尝试评价状态不是 completed 的订单

**请求**
```
POST http://localhost:8005/reviews/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "order_id": 3,  ⚠️ 假设订单3还在进行中
  "stars": 5,
  "content": "Early review"
}
```

**预期响应 400**
```json
{
  "detail": "You can only review completed orders"
}
```

---

### 测试 11: 评价未支付的订单（应失败）

**场景**: 尝试评价已完成但未支付的订单

**预期响应 400**
```json
{
  "detail": "You can only review paid orders"
}
```

---

### 测试 12: 查询不存在的评价

**请求**
```
GET http://localhost:8005/reviews/order/99999
```

**预期响应 404**
```json
{
  "detail": "Review not found for this order"
}
```

---

### 测试 13: 查询不存在的服务商评分

**请求**
```
GET http://localhost:8005/reviews/provider/99999/rating
```

**预期响应 200** (返回默认值)
```json
{
  "provider_id": 99999,
  "average_rating": 5.0,
  "total_reviews": 0
}
```

---

## 🔄 多评价场景测试

### 测试 14: 创建多个评价并验证平均分

**步骤 1: 创建第二个订单并完成**
```
# 1. Customer 创建订单
POST http://localhost:8003/customer/orders/
Authorization: Bearer <customer_token>
{
  "title": "Second cleaning job",
  "description": "Clean kitchen",
  "service_type": "cleaning",
  "price": 80.0,
  "location": "NORTH"
}

# 2. Provider 接受
PUT http://localhost:8003/provider/orders/2/accept
Authorization: Bearer <provider_token>

# 3. Provider 完成
PUT http://localhost:8003/provider/orders/2/complete
Authorization: Bearer <provider_token>

# 4. Customer 支付
POST http://localhost:8004/customer/payments/pay
Authorization: Bearer <customer_token>
{
  "order_id": 2
}
```

**步骤 2: 创建第二个评价（3星）**
```
POST http://localhost:8005/reviews/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "order_id": 2,
  "stars": 3,
  "content": "Good but could be better"
}
```

**步骤 3: 验证平均分更新**
```
GET http://localhost:8005/reviews/provider/<provider_user_id>/rating
```

**预期响应**
```json
{
  "provider_id": 2,
  "average_rating": 4.0,  // (5 + 3) / 2 = 4.0
  "total_reviews": 2
}
```

**步骤 4: 获取所有评价**
```
GET http://localhost:8005/reviews/provider/<provider_user_id>
```

**预期响应**
```json
[
  {
    "order_id": 1,
    "customer_id": 1,
    "stars": 5,
    "content": "Excellent service! Very professional and thorough.",
    "created_at": "2025-10-16T12:00:00Z"
  },
  {
    "order_id": 2,
    "customer_id": 1,
    "stars": 3,
    "content": "Good but could be better",
    "created_at": "2025-10-16T12:05:00Z"
  }
]
```

---

## ✅ 完整测试检查清单

### 基础功能
- [ ] 健康检查返回 200
- [ ] 创建评价成功（5星）
- [ ] 获取服务商评分正确（公开接口）
- [ ] Provider 查看自己的评分（认证接口）
- [ ] 获取服务商所有评价正确（公开接口）
- [ ] Provider 查看自己的所有评价（认证接口）
- [ ] 根据订单获取评价正确

### 权限验证
- [ ] 未认证请求返回 401
- [ ] 非订单所有者评价返回 403
- [ ] 正确的 customer 可以评价自己的订单

### 业务逻辑
- [ ] 重复评价同一订单返回 400
- [ ] 评分范围验证（1-5星）
- [ ] 多个评价后平均分计算正确
- [ ] 总评价数更新正确

### 边界情况
- [ ] 查询不存在的订单评价返回 404
- [ ] 查询不存在的服务商评分返回默认值（5.0, 0）
- [ ] 评价内容为空（可选字段）正常工作

### 数据一致性
- [ ] MongoDB reviews 集合数据正确
- [ ] MongoDB provider_ratings 集合数据正确
- [ ] RabbitMQ 事件正确发布
  - review.created
  - rating.updated

---

## 🔍 验证数据库数据

### 查看 MongoDB 数据
```javascript
// 连接到 MongoDB
use review_db

// 查看所有评价
db.reviews.find().pretty()

// 查看服务商评分
db.provider_ratings.find().pretty()

// 统计评价数量
db.reviews.countDocuments()
```

**预期数据结构**

**reviews 集合**
```json
{
  "order_id": 1,
  "customer_id": 1,
  "provider_id": 2,
  "stars": 5,
  "content": "Excellent service!",
  "created_at": ISODate("2025-10-16T12:00:00.000Z")
}
```

**provider_ratings 集合**
```json
{
  "provider_id": 2,
  "average_rating": 4.0,
  "total_reviews": 2
}
```

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
  "customer_token": "<set_after_login>",
  "provider_token": "<set_after_login>",
  "customer_id": "<set_after_getting_user_info>",
  "provider_id": "<set_after_getting_user_info>",
  "order_id": "<set_after_creating_order>"
}
```

### 使用变量的请求示例
```
POST {{review_url}}/reviews/
Authorization: Bearer {{customer_token}}
Content-Type: application/json

{
  "order_id": {{order_id}},
  "stars": 5,
  "content": "Great service!"
}
```

---

## 🐛 常见错误排查

### 错误 1: 401 Unauthorized
**原因**: Token 无效或未提供
**解决**: 
- 重新登录获取新 token
- 检查 Authorization header 格式: `Bearer <token>`

### 错误 2: 403 Forbidden - "You can only review your own orders"
**原因**: 尝试评价不属于当前用户的订单
**解决**: 
- 确保使用订单所属 customer 的 token
- 不要使用 provider token 评价订单

### 错误 3: 400 Bad Request - "This order has already been reviewed"
**原因**: 该订单已经有评价了
**解决**: 
- 每个订单只能评价一次
- 创建新订单并完成后再评价

### 错误 4: 422 Validation Error - stars
**原因**: 评分不在 1-5 范围内
**解决**: 
- 确保 stars 字段值为 1, 2, 3, 4, 或 5

### 错误 5: 503 Service Unavailable - Auth service unavailable
**原因**: Auth Service 未启动或连接失败
**解决**:
```bash
# 检查 Auth Service 是否运行
lsof -i :8000

# 重启 Auth Service
cd services/auth-service
uvicorn auth_service.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
```

---

## 💡 测试技巧

### 1. 快速获取测试用户信息
```bash
# 保存到环境变量
# Customer
export CUSTOMER_TOKEN="<customer的access_token>"
export CUSTOMER_ID="<customer的user_id>"

# Provider
export PROVIDER_TOKEN="<provider的access_token>"
export PROVIDER_ID="<provider的user_id>"
```

### 2. 使用 Postman Tests 自动提取数据
```javascript
// 在 Login 请求的 Tests 标签页添加
pm.environment.set("customer_token", pm.response.json().access_token);

// 在 Get User Me 请求的 Tests 标签页添加
pm.environment.set("customer_id", pm.response.json().id);

// 在 Create Order 请求的 Tests 标签页添加
pm.environment.set("order_id", pm.response.json().order_id);
```

### 3. 批量测试评分计算
创建多个 1-5 星的评价，验证平均分计算：
- 1个5星 → 平均分 5.0
- 1个5星 + 1个3星 → 平均分 4.0
- 1个5星 + 1个3星 + 1个1星 → 平均分 3.0

---

## 🎯 测试完成标准

全部测试通过条件：
✅ 所有 API 端点响应正确状态码
✅ 创建评价后数据库有对应记录
✅ 服务商评分计算准确
✅ 重复评价被正确拒绝
✅ 权限验证正常工作
✅ 边界情况处理正确
✅ RabbitMQ 事件正常发布

**Review Service 测试完成！🎉**
