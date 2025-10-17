# Gateway Service API 更改摘要

## 📅 更新日期：2025-10-17

## 🔧 主要修复

### 1. JWT Secret Key 统一
- **问题**：Gateway Service 和 Auth Service 的 JWT Secret Key 不一致导致 401 错误
- **修复**：统一为 `auth-service-secret-key-2025`
- **影响文件**：`gateway-service/.env`

### 2. Profile 路由重构
- **问题**：
  - Gateway 调用的路由与 User Service 实际路由不匹配
  - 获取/更新 Profile 返回 404 错误
  - 路由设计不够清晰（混合使用 `/users/profile`）

- **修复**：完全重构 Profile 路由，按角色分离
  
**旧设计（已废弃）**：
```
GET  /api/v1/users/profile      # 获取资料（角色不明确）❌
PUT  /api/v1/users/profile      # 更新资料（角色不明确）❌
POST /api/v1/customer/profile   # 创建客户资料
POST /api/v1/provider/profile   # 创建服务商资料
```

**新设计（当前使用）**：
```
# Customer Profile
POST /api/v1/customer/profile   # 创建客户资料 ✅
GET  /api/v1/customer/profile   # 获取客户资料 ✅
PUT  /api/v1/customer/profile   # 更新客户资料 ✅

# Provider Profile
POST /api/v1/provider/profile   # 创建服务商资料 ✅
GET  /api/v1/provider/profile   # 获取服务商资料 ✅
PUT  /api/v1/provider/profile   # 更新服务商资料 ✅
```

### 3. 后端路由映射
Gateway 现在正确映射到 User Service 的实际端点：

| Gateway 端点 | User Service 端点 | 说明 |
|-------------|------------------|------|
| `POST /api/v1/customer/profile` | `POST /customer/profile/` | 创建客户资料 |
| `GET /api/v1/customer/profile` | `GET /customer/profile/me` | 获取当前客户资料 |
| `PUT /api/v1/customer/profile` | `PUT /customer/profile/me` | 更新当前客户资料 |
| `POST /api/v1/provider/profile` | `POST /provider/profile/` | 创建服务商资料 |
| `GET /api/v1/provider/profile` | `GET /provider/profile/me` | 获取当前服务商资料 |
| `PUT /api/v1/provider/profile` | `PUT /provider/profile/me` | 更新当前服务商资料 |

## 📊 API 端点总览

### 总计：28 个端点
- **需认证**：23 个
- **公开接口**：5 个

### 端点分类

#### 🔐 认证模块（3个）
- `POST /auth/register` - 用户注册（公开）
- `POST /auth/login` - 用户登录（公开）
- `GET /auth/me` - 获取当前用户信息（需认证 + 限流）

#### 👤 Customer Profile（3个）
- `POST /customer/profile` - 创建客户资料（需认证 + 限流）
- `GET /customer/profile` - 获取客户资料（需认证 + 限流）
- `PUT /customer/profile` - 更新客户资料（需认证 + 限流）

#### 👨‍💼 Provider Profile（3个）
- `POST /provider/profile` - 创建服务商资料（需认证 + 限流）
- `GET /provider/profile` - 获取服务商资料（需认证 + 限流）
- `PUT /provider/profile` - 更新服务商资料（需认证 + 限流）

#### 📦 Customer 订单（3个）
- `POST /customer/orders/publish` - 发布订单（需认证 + 限流）
- `GET /customer/orders` - 获取订单列表（需认证 + 限流）
- `POST /customer/orders/cancel/{order_id}` - 取消订单（需认证 + 限流）

#### 💰 Customer 支付（3个）
- `POST /customer/payments/recharge` - 充值余额（需认证 + 限流）
- `POST /customer/payments/pay` - 支付订单（需认证 + 限流）
- `GET /customer/payments/transactions` - 查询交易记录（需认证 + 限流）

#### 📬 Customer 通知（1个）
- `GET /customer/inbox` - 获取客户收件箱（需认证 + 限流）

#### 🛠️ Provider 订单（4个）
- `GET /provider/orders/available` - 获取可接单列表（需认证 + 限流）
- `POST /provider/orders/accept/{order_id}` - 接受订单（需认证 + 限流）
- `POST /provider/orders/status/{order_id}` - 更新订单状态（需认证 + 限流）
- `GET /provider/orders` - 获取服务商订单列表（需认证 + 限流）

#### 📬 Provider 通知（1个）
- `GET /provider/inbox` - 获取服务商收件箱（需认证 + 限流）

#### ⭐ 评价模块（5个）
- `POST /reviews` - 创建评价（需认证 + 限流）
- `GET /reviews/provider/me/rating` - 获取我的评分（需认证 + 限流）
- `GET /reviews/provider/me/reviews` - 获取我的评价列表（需认证 + 限流）
- `GET /reviews/provider/{provider_id}/rating` - 获取服务商评分（公开）
- `GET /reviews/provider/{provider_id}` - 获取服务商评价列表（公开）

#### 🏥 系统端点（2个）
- `GET /health` - 健康检查（公开）
- `GET /` - 根路径（公开）

## 🔄 迁移指南

### 如果你在使用旧的 API 端点，请按以下方式更新：

#### 获取用户资料
```diff
- GET /api/v1/users/profile
+ GET /api/v1/customer/profile  （Customer）
+ GET /api/v1/provider/profile  （Provider）
```

#### 更新用户资料
```diff
- PUT /api/v1/users/profile
+ PUT /api/v1/customer/profile  （Customer）
+ PUT /api/v1/provider/profile  （Provider）
```

### Postman 环境变量更新

```json
{
  "gateway_url": "http://localhost:8080/api/v1",
  "customer_token": "{{access_token}}",
  "provider_token": "{{access_token}}"
}
```

## ✅ 优势

1. **路由清晰**：Customer 和 Provider 端点完全分离
2. **RESTful 设计**：同一资源的 CRUD 操作使用相同路径，不同 HTTP 方法
3. **易于维护**：代码结构更清晰，职责分明
4. **类型安全**：通过端点即可识别用户角色
5. **完整功能**：所有业务操作都可通过 Gateway 完成

## 🎯 完整业务流程

现在可以完全通过 Gateway 完成端到端的业务流程：

```
1. 注册/登录 (Customer/Provider)
2. 创建 Profile
3. 充值余额 (Customer)
4. 发布订单 (Customer)
5. 查看/接单 (Provider)
6. 完成订单 (Provider)
7. 支付订单 (Customer)
8. 创建评价 (Customer)
9. 查看评分/评价 (Provider)
10. 查询交易记录
11. 查看通知
```

**所有步骤均通过 Gateway 完成，无需直接访问后端服务！** ✅

## 📚 相关文档

- [完整测试指南](./POSTMAN_TEST_GUIDE.md)
- [快速测试参考](./QUICK_TEST_REFERENCE.md)

## 🐛 故障排除

### 401 Unauthorized 错误
- **原因**：JWT Secret Key 不一致
- **解决**：确认 Gateway 的 `.env` 文件中 `SECRET_KEY=auth-service-secret-key-2025`

### 404 Not Found 错误
- **原因**：使用了旧的 `/users/profile` 端点
- **解决**：改用新的 `/customer/profile` 或 `/provider/profile` 端点

### Profile 无法返回
- **原因**：Gateway 路由配置不正确
- **解决**：确认已更新到最新的 Gateway 代码

## 🚀 测试建议

1. 重启 Gateway Service 确保配置生效
2. 先测试健康检查：`GET /health`
3. 注册并登录获取 token
4. 测试 Profile CRUD 操作
5. 测试完整业务流程

---

**更新完成！** 🎉 现在 Gateway Service 提供完整、清晰、易用的 API 接口。
