# Notification Service 快速测试参考

## 🚀 一键测试命令

```bash
# 确认服务运行
lsof -i :8006  # Notification Service

# 健康检查
curl http://localhost:8006/health
```

---

## 📋 核心端点

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/health` | GET | ❌ | 健康检查 |
| `/customer/inbox/` | GET | ✅ Customer | 获取客户收件箱 |
| `/provider/inbox/` | GET | ✅ Provider | 获取服务商收件箱 |

---

## 🎯 快速测试流程（6 步）

### 1️⃣ 健康检查
```bash
GET http://localhost:8006/health
→ 期望: 200 OK
```

### 2️⃣ 创建测试用户并登录
```bash
# Customer
POST /auth/register + /auth/login
→ 保存: customer_token

# Provider
POST /auth/register + /auth/login
→ 保存: provider_token
```

### 3️⃣ 创建 Profiles
```bash
POST /customer/profile/ (customer_token)
POST /provider/profile/ (provider_token)
```

### 4️⃣ 触发订单事件 → 验证通知
```bash
# 创建订单
POST /customer/orders/ (customer_token)

# 查看 Customer 收件箱
GET /customer/inbox/ (customer_token)
→ 期望: 1 条通知 "订单创建成功"

# Provider 接受订单
PUT /provider/orders/{id}/accept (provider_token)

# 查看 Customer 收件箱
GET /customer/inbox/ (customer_token)
→ 期望: 2 条通知（新增"订单被接受"）

# 查看 Provider 收件箱
GET /provider/inbox/ (provider_token)
→ 期望: 1 条通知 "成功接受订单"
```

### 5️⃣ 触发支付事件 → 验证通知
```bash
# 充值 + 完成订单 + 支付
POST /customer/payments/recharge (customer_token)
PUT /provider/orders/{id}/complete (provider_token)
POST /customer/payments/pay (customer_token)

# 查看 Customer 收件箱
GET /customer/inbox/ (customer_token)
→ 期望: 3 条通知（新增"支付成功"）

# 查看 Provider 收件箱
GET /provider/inbox/ (provider_token)
→ 期望: 2 条通知（新增"收到付款"）
```

### 6️⃣ 触发评价事件 → 验证通知
```bash
# 创建评价
POST /reviews/ (customer_token)

# 查看 Customer 收件箱
GET /customer/inbox/ (customer_token)
→ 期望: 4 条通知（新增"评价创建成功"）

# 查看 Provider 收件箱
GET /provider/inbox/ (provider_token)
→ 期望: 3 条通知（新增"收到 5 星评价"）
```

---

## ✅ 最终验证清单

**完整业务流程后的预期结果：**

| 角色 | 通知总数 | 通知内容 |
|------|---------|---------|
| Customer | 4 条 | ① 订单创建<br>② 订单被接受<br>③ 支付成功<br>④ 评价创建 |
| Provider | 3 条 | ① 接受订单<br>② 收到付款<br>③ 收到评价 |

---

## 🔧 故障排查

### 问题: 收件箱为空
```bash
# 检查 RabbitMQ
lsof -i :5672
# 检查 MongoDB
lsof -i :27017
# 检查 Notification Service 日志
# 应该看到: ✅ Connected to RabbitMQ
```

### 问题: 通知延迟
- 等待 2-3 秒（异步处理）
- 检查 RabbitMQ 管理界面: http://localhost:15672

### 问题: 401 Unauthorized
- 重新登录获取新 token
- 检查 Authorization header 格式

---

## 📊 MongoDB 快速查询

```javascript
// 连接
use notification_db

// 查看所有通知
db.customer_inbox.find().pretty()
db.provider_inbox.find().pretty()

// 统计数量
db.customer_inbox.countDocuments()
db.provider_inbox.countDocuments()
```

---

## 🎯 Postman 环境变量

```json
{
  "notification_url": "http://localhost:8006",
  "customer_token": "<从登录获取>",
  "provider_token": "<从登录获取>",
  "order_id": "<从创建订单获取>"
}
```

---

## ⚡ 测试技巧

1. **异步延迟**: 触发事件后等待 2 秒再查询收件箱
2. **顺序执行**: 按照完整流程测试，不要跳步骤
3. **多次验证**: 每次操作后都验证收件箱，确认新通知
4. **数据库验证**: 用 MongoDB 命令行验证数据持久化

---

**测试完成！** ✨
