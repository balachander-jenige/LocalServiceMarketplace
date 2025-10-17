# Gateway Service 快速测试参考

## 🚀 快速启动

```bash
# 1. 确认所有后端服务运行
lsof -i :8000 :8002 :8003 :8004 :8005 :8006

# 2. 启动 Gateway
cd gateway-service
uvicorn gateway_service.main:app --reload --host 0.0.0.0 --port 8080 --app-dir src

# 3. 健康检查
curl http://localhost:8080/health
```

---

## 📌 核心端点速查表

**Base URL**: `http://localhost:8080/api/v1`

| 分类 | 端点 | 方法 | 认证 | 限流 | 说明 |
|------|------|------|------|------|------|
| **Auth** | `/auth/register` | POST | ❌ | ❌ | 用户注册 |
| | `/auth/login` | POST | ❌ | ❌ | 用户登录 |
| | `/auth/me` | GET | ✅ | ✅ | 获取当前用户 |
| **Customer** | `/customer/profile` | POST | ✅ | ✅ | 创建资料 |
| | `/customer/profile` | GET | ✅ | ✅ | 获取资料 |
| | `/customer/profile` | PUT | ✅ | ✅ | 更新资料 |
| | `/customer/orders/publish` | POST | ✅ | ✅ | 发布订单 |
| | `/customer/orders` | GET | ✅ | ✅ | 订单列表 |
| | `/customer/orders/cancel/{id}` | POST | ✅ | ✅ | 取消订单 |
| | `/customer/inbox` | GET | ✅ | ✅ | 收件箱 |
| | `/customer/payments/recharge` | POST | ✅ | ✅ | 充值余额 |
| | `/customer/payments/pay` | POST | ✅ | ✅ | 支付订单 |
| | `/customer/payments/transactions` | GET | ✅ | ✅ | 交易记录 |
| **Provider** | `/provider/profile` | POST | ✅ | ✅ | 创建资料 |
| | `/provider/profile` | GET | ✅ | ✅ | 获取资料 |
| | `/provider/profile` | PUT | ✅ | ✅ | 更新资料 |
| | `/provider/orders/available` | GET | ✅ | ✅ | 可接单列表 |
| | `/provider/orders/accept/{id}` | POST | ✅ | ✅ | 接受订单 |
| | `/provider/orders/status/{id}` | POST | ✅ | ✅ | 更新状态 |
| | `/provider/orders` | GET | ✅ | ✅ | 订单列表 |
| | `/provider/inbox` | GET | ✅ | ✅ | 收件箱 |
| **Review** | `/reviews` | POST | ✅ | ✅ | 创建评价 |
| | `/reviews/provider/me/rating` | GET | ✅ | ✅ | 我的评分 |
| | `/reviews/provider/me/reviews` | GET | ✅ | ✅ | 我的评价 |
| | `/reviews/provider/{id}/rating` | GET | ❌ | ❌ | 服务商评分 |
| | `/reviews/provider/{id}` | GET | ❌ | ❌ | 服务商评价 |

**总计**: 28 个端点

---

## 🎯 5 分钟快速测试

### 1️⃣ 健康检查
```bash
GET http://localhost:8080/health
→ 200 OK
```

### 2️⃣ 注册并登录
```bash
# 注册 Customer
POST /api/v1/auth/register
{
  "username": "customer_gw",
  "email": "customer_gw@test.com",
  "password": "Test123456",
  "role": "customer"
}

# 登录
POST /api/v1/auth/login
{
  "username": "customer_gw",
  "password": "Test123456"
}
→ 保存 token
```

### 3️⃣ 创建并获取 Profile
```bash
# 创建 Customer Profile
POST /api/v1/customer/profile
Authorization: Bearer <token>
{
  "location": "NORTH",
  "address": "123 Test St",
  "budget_preference": 1000
}

# 获取 Customer Profile
GET /api/v1/customer/profile
Authorization: Bearer <token>
→ 验证: Gateway 正确转发到 User Service
```

### 4️⃣ 测试认证和路由
```bash
# 获取当前用户（需认证 + 限流）
GET /api/v1/auth/me
Authorization: Bearer <token>
→ 验证: Gateway 正确转发到 Auth Service
```

### 5️⃣ 测试统一响应格式
```bash
# 所有成功响应应该是:
{
  "success": true,
  "data": { ... },
  "message": "...",
  "error": null
}
```

### 6️⃣ 测试限流
```bash
# 快速发送 61 次请求
# 前 60 次: 200 OK
# 第 61 次: 429 Too Many Requests
```

---

## ✅ 统一响应格式

**成功响应**:
```json
{
  "success": true,
  "data": { /* 实际业务数据 */ },
  "message": "Success" // 或其他提示,
  "error": null
}
```

**失败响应**:
```json
{
  "detail": "错误描述"
}
```

---

## 🔐 认证格式

所有需要认证的端点:
```
Authorization: Bearer <your_jwt_token>
```

---

## 🧪 关键测试场景

### 场景 1: 完整订单流程 ⭐ 已增强

```bash
1. Customer 注册登录 → /api/v1/auth/*
2. Provider 注册登录 → /api/v1/auth/*
3. Customer 创建资料 → /api/v1/customer/profile
4. Provider 创建资料 → /api/v1/provider/profile
5. Customer 充值余额 → /api/v1/customer/payments/recharge
6. Customer 发布订单 → /api/v1/customer/orders/publish
7. Provider 查看订单 → /api/v1/provider/orders/available
8. Provider 接受订单 → /api/v1/provider/orders/accept/{id}
9. Provider 完成订单 → /api/v1/provider/orders/status/{id}
10. Customer 支付订单 → /api/v1/customer/payments/pay
11. Customer 创建评价 → /api/v1/reviews
12. Provider 查看评分 → /api/v1/reviews/provider/me/rating
13. Provider 查看评价 → /api/v1/reviews/provider/me/reviews
14. 查询交易记录 → /api/v1/customer/payments/transactions
15. 查看服务商评分 → /api/v1/reviews/provider/{id}/rating
16. Customer 查看通知 → /api/v1/customer/inbox
17. Provider 查看通知 → /api/v1/provider/inbox
```

**预期**: 所有步骤通过 Gateway 正常完成 ✅

---

### 场景 2: 安全性测试

```bash
# 1. 未认证访问
GET /api/v1/auth/me
→ 403 Not authenticated

# 2. 无效 Token
Authorization: Bearer invalid_token
→ 401 Invalid token

# 3. 限流测试
快速发送 61 次请求
→ 第 61 次返回 429 Rate limit exceeded
```

---

### 场景 3: 统一格式验证

```bash
# 所有成功响应都应该包含:
✅ success: true
✅ data: { ... }
✅ message: "..."
✅ error: null
```

---

## 🐛 快速排查

| 错误 | 状态码 | 原因 | 解决方案 |
|------|--------|------|----------|
| Service unavailable | 503 | 后端服务未启动 | 启动对应服务 |
| Not authenticated | 403 | 缺少 Auth header | 添加 `Authorization: Bearer <token>` |
| Invalid token | 401 | Token 无效/过期 | 重新登录 |
| Rate limit exceeded | 429 | 超过 60次/分钟 | 等待 1 分钟 |

---

## 📊 Postman 环境变量

```json
{
  "gateway_url": "http://localhost:8080",
  "customer_token": "<登录后保存>",
  "provider_token": "<登录后保存>",
  "order_id": "<创建订单后保存>"
}
```

---

## 🎯 测试验证清单

**Gateway 核心功能**:
- [ ] 健康检查正常
- [ ] 请求正确路由到后端服务
- [ ] JWT 认证中间件工作
- [ ] 限流中间件工作 (60次/分钟)
- [ ] 统一响应格式应用
- [ ] 错误处理正常
- [ ] Token 正确传递到后端

**端点覆盖**:
- [ ] 认证端点 (3个)
- [ ] Customer Profile 端点 (3个) - 创建/获取/更新
- [ ] Provider Profile 端点 (3个) - 创建/获取/更新
- [ ] Customer 订单端点 (3个)
- [ ] Customer 支付端点 (3个) - 充值/支付/查询
- [ ] Provider 订单端点 (4个)
- [ ] Provider 评价端点 (2个) - 自查评分/评价
- [ ] 评价端点 (3个)
- [ ] 通知端点 (2个)

**总计**: 28 个端点

---

## 💡 重要提示

### ✅ Gateway 功能已完善

所有核心业务功能均已暴露在 Gateway：
- ✅ Profile 创建（Customer & Provider）
- ✅ 支付功能（充值、支付、查询）
- ✅ Provider 自查功能（评分、评价）
- ✅ 完整的订单流程
- ✅ 通知查询

### 测试注意事项

1. **限流重置**: 1 分钟后自动重置
2. **Token 过期**: 默认 30 分钟过期
3. **异步通知**: 通知可能有 2-3 秒延迟
4. **统一格式**: 所有响应都应该有 `success` 字段
5. **路由顺序**: `/me` 路由优先于 `/{id}` 路由匹配

---

## 🚀 下一步

1. ✅ 完成 Gateway 基础功能测试
2. 📝 补充缺失的端点映射
3. 🔧 统一支付端点设计
4. 🎨 前端集成测试
5. 🔐 添加更细粒度的权限控制

---

**Gateway Service 测试快速参考完成！** ⚡
