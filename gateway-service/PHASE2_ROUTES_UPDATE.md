# Gateway Service - 第二阶段路由更新总结

## 📋 新增的管理员订单路由

### 1. 获取所有订单
```http
GET /admin/orders?status={status}
Authorization: Bearer {ADMIN_TOKEN}
```
- **权限**: 需要管理员 Token (role_id = 3)
- **参数**: 
  - `status` (可选): 过滤订单状态 (pending_review, pending, accepted, etc.)
- **返回**: 所有订单列表

---

### 2. 获取待审核订单
```http
GET /admin/orders/pending-review
Authorization: Bearer {ADMIN_TOKEN}
```
- **权限**: 需要管理员 Token
- **返回**: 所有 `pending_review` 状态的订单

---

### 3. 获取订单详情
```http
GET /admin/orders/{order_id}
Authorization: Bearer {ADMIN_TOKEN}
```
- **权限**: 需要管理员 Token
- **返回**: 订单完整详情(包含 service_type, service_start_time, service_end_time)

---

### 4. 审批订单
```http
POST /admin/orders/{order_id}/approve
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json

{
  "approved": true,  // 或 false
  "reject_reason": "拒绝原因"  // approved=false 时必填
}
```
- **权限**: 需要管理员 Token
- **功能**: 
  - `approved: true` → 订单状态变为 `pending`
  - `approved: false` → 订单状态变为 `cancelled`

---

### 5. 更新订单信息
```http
PUT /admin/orders/{order_id}
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json

{
  "title": "新标题",
  "price": 250.00,
  "service_type": "it_technology",
  "service_start_time": "2025-10-26T10:00:00",
  // ... 其他可选字段
}
```
- **权限**: 需要管理员 Token
- **功能**: 更新订单的任意字段

---

### 6. 删除订单
```http
DELETE /admin/orders/{order_id}
Authorization: Bearer {ADMIN_TOKEN}
```
- **权限**: 需要管理员 Token
- **功能**: 永久删除订单

---

## 🔐 权限验证机制

所有管理员路由都使用 `verify_admin_token()` 中间件:
- 验证 JWT Token 有效性
- 检查 Token 中的 `role` 字段是否为 `3` (管理员)
- 如果不是管理员,返回 `403 Forbidden`

---

## 📝 修改的文件

### 1. `order_client.py`
新增方法:
- ✅ `get_all_orders()`
- ✅ `get_pending_review_orders()`
- ✅ `get_order_detail_admin()`
- ✅ `approve_order()`
- ✅ `update_order_admin()`
- ✅ `delete_order_admin()`

### 2. `routes.py`
新增路由:
- ✅ `GET /admin/orders`
- ✅ `GET /admin/orders/pending-review`
- ✅ `GET /admin/orders/{order_id}`
- ✅ `POST /admin/orders/{order_id}/approve`
- ✅ `PUT /admin/orders/{order_id}`
- ✅ `DELETE /admin/orders/{order_id}`

### 3. `middleware.py`
已有 `verify_admin_token()` 中间件,无需修改

---

## 🧪 Postman 测试更新

现在可以通过 Gateway (8080端口) 测试管理员功能:

### 测试示例:

#### 1. 管理员登录
```http
POST http://localhost:8080/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin123!"
}
```
保存返回的 `access_token`

#### 2. 获取待审核订单
```http
GET http://localhost:8080/admin/orders/pending-review
Authorization: Bearer {ADMIN_TOKEN}
```

#### 3. 审批订单
```http
POST http://localhost:8080/admin/orders/1/approve
Authorization: Bearer {ADMIN_TOKEN}
Content-Type: application/json

{
  "approved": true
}
```

---

## ✅ 完成清单

- ✅ Order Client 添加管理员方法
- ✅ Gateway Routes 添加管理员路由
- ✅ 所有管理员路由使用 `verify_admin_token()` 保护
- ✅ 支持按状态过滤订单
- ✅ 支持订单审批(批准/拒绝)
- ✅ 支持订单 CRUD 操作

---

## 🔄 完整的订单流程(通过 Gateway)

1. **客户发布订单**
   ```
   POST /customer/orders/publish → pending_review
   ```

2. **管理员查看待审核订单**
   ```
   GET /admin/orders/pending-review
   ```

3. **管理员审批订单**
   ```
   POST /admin/orders/{id}/approve → pending
   ```

4. **服务商接单**
   ```
   POST /provider/orders/accept/{id} → accepted
   ```

5. **更新订单状态**
   ```
   POST /provider/orders/status/{id} → in_progress → completed
   ```

6. **客户评价**
   ```
   POST /reviews → reviewed
   ```

---

现在所有第二阶段的接口都已经添加到 Gateway Service! 🎉
