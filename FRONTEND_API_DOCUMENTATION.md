# 前端接口文档 (Frontend API Documentation)

## 📋 文档说明

本文档为前端开发者提供完整的 API 接口说明，包括所有可用的接口、请求格式、响应格式和使用示例。

**版本**: v1.0  
**最后更新**: 2025-10-17  
**基础地址**: `http://localhost:8080/api/v1`  
**协议**: HTTP/HTTPS  
**数据格式**: JSON

---

## 🔑 认证说明

### 认证方式

除标注为"公开接口"外，所有接口都需要携带 JWT Token 进行认证。

### 如何获取 Token

1. 通过 `/auth/register` 注册账号
2. 通过 `/auth/login` 登录获取 Token
3. 在后续请求的 Header 中携带 Token

### Token 使用方法

```
Authorization: Bearer <your_token_here>
```

### Token 有效期

- Token 有效期：30 分钟
- Token 过期后需要重新登录获取新 Token

---

## 📊 统一响应格式

所有接口都遵循统一的响应格式：

### 成功响应

```json
{
  "success": true,
  "data": {
    // 实际业务数据
  },
  "message": "操作成功提示信息",
  "error": null
}
```

### 失败响应

```json
{
  "success": false,
  "data": null,
  "message": "错误描述",
  "error": "详细错误信息"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token 无效或过期）|
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 429 | 请求过于频繁（限流）|
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

---

## 🎭 用户角色

系统支持两种用户角色：

| 角色 ID | 角色名称 | 说明 |
|---------|----------|------|
| 1 | Customer | 客户（发布订单、支付）|
| 2 | Provider | 服务商（接单、提供服务）|

---

## 📚 接口列表

### 1. 认证模块 (Authentication)

#### 1.1 用户注册

**接口地址**: `POST /auth/register`  
**认证要求**: ❌ 无需认证（公开接口）  
**接口说明**: 注册新用户账号

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | ✅ | 用户名 |
| email | string | ✅ | 邮箱（需符合邮箱格式）|
| password | string | ✅ | 密码 |
| role_id | integer | ✅ | 角色 ID（1=Customer, 2=Provider）|

**请求示例**:

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "role_id": 1
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "message": "Registration successful",
  "error": null
}
```

---

#### 1.2 用户登录

**接口地址**: `POST /auth/login`  
**认证要求**: ❌ 无需认证（公开接口）  
**接口说明**: 用户登录获取访问令牌

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| email | string | ✅ | 注册时使用的邮箱 |
| password | string | ✅ | 密码 |

**请求示例**:

```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "message": "Login successful",
  "error": null
}
```

**重要**: 请保存 `access_token`，后续所有需要认证的接口都需要携带此 Token。

---

#### 1.3 获取当前用户信息

**接口地址**: `GET /auth/me`  
**认证要求**: ✅ 需要认证  
**接口说明**: 获取当前登录用户的基本信息

**请求 Header**:

```
Authorization: Bearer <your_token>
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role_id": 1
  },
  "message": "Success",
  "error": null
}
```

---

### 2. 客户资料模块 (Customer Profile)

#### 2.1 创建客户资料

**接口地址**: `POST /customer/profile`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 创建客户用户的详细资料

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 | 默认值 |
|--------|------|------|------|--------|
| location | string | ❌ | 所在地区 | "NORTH" |
| address | string | ❌ | 详细地址 | null |
| budget_preference | number | ❌ | 预算偏好 | 0.0 |

**location 可选值**: `NORTH`, `SOUTH`, `EAST`, `WEST`, `CENTRAL`

**请求示例**:

```json
{
  "location": "NORTH",
  "address": "123 Main Street",
  "budget_preference": 1000.0
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "location": "NORTH",
    "address": "123 Main Street",
    "budget_preference": 1000.0,
    "balance": 0.0,
    "created_at": "2025-10-17T10:00:00",
    "updated_at": "2025-10-17T10:00:00"
  },
  "message": "Customer profile created",
  "error": null
}
```

---

#### 2.2 获取客户资料

**接口地址**: `GET /customer/profile`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 获取当前客户用户的资料信息

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "location": "NORTH",
    "address": "123 Main Street",
    "budget_preference": 1000.0,
    "balance": 500.0,
    "created_at": "2025-10-17T10:00:00",
    "updated_at": "2025-10-17T11:00:00"
  },
  "message": "Success",
  "error": null
}
```

---

#### 2.3 更新客户资料

**接口地址**: `PUT /customer/profile`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 更新客户用户的资料信息（所有字段可选）

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | ❌ | 所在地区 |
| address | string | ❌ | 详细地址 |
| budget_preference | number | ❌ | 预算偏好 |

**请求示例**:

```json
{
  "address": "456 New Street",
  "budget_preference": 2000.0
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "location": "NORTH",
    "address": "456 New Street",
    "budget_preference": 2000.0,
    "balance": 500.0,
    "created_at": "2025-10-17T10:00:00",
    "updated_at": "2025-10-17T12:00:00"
  },
  "message": "Customer profile updated",
  "error": null
}
```

---

### 3. 服务商资料模块 (Provider Profile)

#### 3.1 创建服务商资料

**接口地址**: `POST /provider/profile`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 创建服务商用户的详细资料

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 | 默认值 |
|--------|------|------|------|--------|
| skills | array[string] | ❌ | 技能列表 | [] |
| experience_years | integer | ❌ | 从业年限 | 0 |
| hourly_rate | number | ❌ | 时薪（单位：元）| 0.0 |
| availability | string | ❌ | 可用时间描述 | null |

**请求示例**:

```json
{
  "skills": ["清洁", "维修", "搬运"],
  "experience_years": 5,
  "hourly_rate": 50.0,
  "availability": "周一至周五 9:00-18:00"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 2,
    "skills": ["清洁", "维修", "搬运"],
    "experience_years": 5,
    "hourly_rate": 50.0,
    "availability": "周一至周五 9:00-18:00",
    "portfolio": [],
    "total_earnings": 0.0,
    "rating": 0.0,
    "total_reviews": 0,
    "created_at": "2025-10-17T10:00:00",
    "updated_at": "2025-10-17T10:00:00"
  },
  "message": "Provider profile created",
  "error": null
}
```

---

#### 3.2 获取服务商资料

**接口地址**: `GET /provider/profile`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 获取当前服务商用户的资料信息

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 2,
    "skills": ["清洁", "维修", "搬运"],
    "experience_years": 5,
    "hourly_rate": 50.0,
    "availability": "周一至周五 9:00-18:00",
    "portfolio": [],
    "total_earnings": 1500.0,
    "rating": 4.8,
    "total_reviews": 15,
    "created_at": "2025-10-17T10:00:00",
    "updated_at": "2025-10-17T11:00:00"
  },
  "message": "Success",
  "error": null
}
```

---

#### 3.3 更新服务商资料

**接口地址**: `PUT /provider/profile`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 更新服务商用户的资料信息（所有字段可选）

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skills | array[string] | ❌ | 技能列表 |
| experience_years | integer | ❌ | 从业年限 |
| hourly_rate | number | ❌ | 时薪 |
| availability | string | ❌ | 可用时间 |
| portfolio | array[string] | ❌ | 作品集链接 |

**请求示例**:

```json
{
  "hourly_rate": 60.0,
  "portfolio": ["https://example.com/work1", "https://example.com/work2"]
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 2,
    "skills": ["清洁", "维修", "搬运"],
    "experience_years": 5,
    "hourly_rate": 60.0,
    "availability": "周一至周五 9:00-18:00",
    "portfolio": ["https://example.com/work1", "https://example.com/work2"],
    "total_earnings": 1500.0,
    "rating": 4.8,
    "total_reviews": 15,
    "created_at": "2025-10-17T10:00:00",
    "updated_at": "2025-10-17T12:00:00"
  },
  "message": "Provider profile updated",
  "error": null
}
```

---

### 4. 订单模块 - 客户端 (Customer Orders)

#### 4.1 发布订单

**接口地址**: `POST /customer/orders/publish`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 客户发布新的服务订单

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | ✅ | 订单标题（不能为空）|
| description | string | ❌ | 订单详细描述 |
| price | number | ✅ | 订单金额（必须>0）|
| location | string | ✅ | 服务地点 |
| address | string | ❌ | 详细地址 |

**请求示例**:

```json
{
  "title": "家庭清洁服务",
  "description": "需要对100平米的房屋进行深度清洁",
  "price": 200.0,
  "location": "NORTH",
  "address": "123 Main Street, Apt 5"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "order_id": 1,
    "status": "pending",
    "message": "Order published successfully."
  },
  "message": "Order published",
  "error": null
}
```

---

#### 4.2 获取进行中的订单

**接口地址**: `GET /customer/orders`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 获取客户当前进行中的订单列表（不包括已完成、已取消）

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "家庭清洁服务",
      "status": "accepted",
      "price": 200.0,
      "location": "NORTH",
      "created_at": "2025-10-17T10:00:00"
    },
    {
      "id": 2,
      "title": "空调维修",
      "status": "pending",
      "price": 150.0,
      "location": "NORTH",
      "created_at": "2025-10-17T11:00:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

**订单状态说明**:

| 状态 | 说明 |
|------|------|
| pending | 待接单 |
| accepted | 已接单（服务商已接单）|
| in_progress | 进行中 |
| completed | 已完成 |
| cancelled | 已取消 |
| paid | 已支付 |

---

#### 4.3 获取订单历史

**接口地址**: `GET /customer/orders/history`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 获取客户的所有历史订单（包括已完成、已取消的订单）

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 10,
      "title": "家具搬运",
      "status": "completed",
      "price": 300.0,
      "location": "SOUTH",
      "created_at": "2025-09-15T10:00:00"
    },
    {
      "id": 8,
      "title": "管道维修",
      "status": "cancelled",
      "price": 180.0,
      "location": "NORTH",
      "created_at": "2025-09-10T14:00:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

---

#### 4.4 取消订单

**接口地址**: `POST /customer/orders/cancel/{order_id}`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 客户取消自己发布的订单

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求示例**:

```
POST /customer/orders/cancel/1
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "order_id": 1,
    "status": "cancelled",
    "message": "Order cancelled successfully."
  },
  "message": "Order cancelled",
  "error": null
}
```

---

### 5. 订单模块 - 服务商端 (Provider Orders)

#### 5.1 获取可接单列表

**接口地址**: `GET /provider/orders/available`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 获取当前可以接的订单列表（状态为 pending 的订单）

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "title": "家电维修",
      "status": "pending",
      "price": 250.0,
      "location": "EAST",
      "created_at": "2025-10-17T12:00:00"
    },
    {
      "id": 4,
      "title": "房屋清洁",
      "status": "pending",
      "price": 180.0,
      "location": "NORTH",
      "created_at": "2025-10-17T12:30:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

---

#### 5.2 接受订单

**接口地址**: `POST /provider/orders/accept/{order_id}`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 服务商接受订单

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求示例**:

```
POST /provider/orders/accept/3
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "order_id": 3,
    "status": "accepted",
    "message": "Order accepted successfully."
  },
  "message": "Order accepted",
  "error": null
}
```

---

#### 5.3 更新订单状态

**接口地址**: `POST /provider/orders/status/{order_id}`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 服务商更新订单状态（如标记为进行中、已完成等）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | ✅ | 新状态 |

**可用状态**: `in_progress`, `completed`

**请求示例**:

```json
{
  "status": "completed"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "order_id": 3,
    "status": "completed",
    "message": "Order status updated successfully."
  },
  "message": "Order status updated",
  "error": null
}
```

---

#### 5.4 获取订单历史

**接口地址**: `GET /provider/orders/history`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 获取服务商的所有历史订单

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "title": "家电维修",
      "status": "completed",
      "price": 250.0,
      "location": "EAST",
      "created_at": "2025-10-17T12:00:00"
    },
    {
      "id": 5,
      "title": "家具组装",
      "status": "completed",
      "price": 200.0,
      "location": "WEST",
      "created_at": "2025-10-16T10:00:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

---

### 6. 支付模块 (Payment)

#### 6.1 充值余额

**接口地址**: `POST /customer/payments/recharge`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 客户为账户充值

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| amount | number | ✅ | 充值金额（必须>0）|

**请求示例**:

```json
{
  "amount": 500.0
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "transaction_id": 1,
    "balance": 500.0,
    "message": "Balance recharged successfully."
  },
  "message": "Recharge successful",
  "error": null
}
```

---

#### 6.2 支付订单

**接口地址**: `POST /customer/payments/pay`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 客户支付订单费用

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求示例**:

```json
{
  "order_id": 3
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "payment_id": 2,
    "order_id": 3,
    "balance": 250.0,
    "message": "Payment successful."
  },
  "message": "Payment successful",
  "error": null
}
```

**注意事项**:
- 支付前请确保账户余额充足
- 只能支付状态为 `completed` 的订单
- 支付成功后订单状态会变为 `paid`

---

### 7. 评价模块 (Review)

#### 7.1 创建评价

**接口地址**: `POST /reviews`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 客户对已完成的订单进行评价

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |
| stars | integer | ✅ | 评分（1-5星）|
| content | string | ❌ | 评价内容 |

**请求示例**:

```json
{
  "order_id": 3,
  "stars": 5,
  "content": "服务非常好，态度认真负责，强烈推荐！"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "review_id": "1",
    "order_id": 3,
    "stars": 5,
    "content": "服务非常好，态度认真负责，强烈推荐！",
    "message": "Review created successfully."
  },
  "message": "Review created",
  "error": null
}
```

---

#### 7.2 获取我的评分（服务商）

**接口地址**: `GET /reviews/provider/me/rating`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 服务商查询自己的平均评分和评价总数

**响应示例**:

```json
{
  "success": true,
  "data": {
    "provider_id": 2,
    "average_rating": 4.8,
    "total_reviews": 15
  },
  "message": "Success",
  "error": null
}
```

---

#### 7.3 获取我的评价列表（服务商）

**接口地址**: `GET /reviews/provider/me/reviews`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 服务商查询自己收到的所有评价

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "order_id": 3,
      "customer_id": 1,
      "stars": 5,
      "content": "服务非常好，态度认真负责，强烈推荐！",
      "created_at": "2025-10-17T15:00:00"
    },
    {
      "order_id": 5,
      "customer_id": 4,
      "stars": 4,
      "content": "服务质量不错，按时完成。",
      "created_at": "2025-10-16T12:00:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

---

#### 7.4 获取服务商评分（公开）

**接口地址**: `GET /reviews/provider/{provider_id}/rating`  
**认证要求**: ❌ 无需认证（公开接口）  
**接口说明**: 查询指定服务商的评分信息（任何人都可以查询）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| provider_id | integer | ✅ | 服务商用户 ID |

**请求示例**:

```
GET /reviews/provider/2/rating
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "provider_id": 2,
    "average_rating": 4.8,
    "total_reviews": 15
  },
  "message": "Success",
  "error": null
}
```

---

#### 7.5 获取服务商评价列表（公开）

**接口地址**: `GET /reviews/provider/{provider_id}`  
**认证要求**: ❌ 无需认证（公开接口）  
**接口说明**: 查询指定服务商的所有评价（任何人都可以查询）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| provider_id | integer | ✅ | 服务商用户 ID |

**请求示例**:

```
GET /reviews/provider/2
```

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "order_id": 3,
      "customer_id": 1,
      "stars": 5,
      "content": "服务非常好，态度认真负责，强烈推荐！",
      "created_at": "2025-10-17T15:00:00"
    },
    {
      "order_id": 5,
      "customer_id": 4,
      "stars": 4,
      "content": "服务质量不错，按时完成。",
      "created_at": "2025-10-16T12:00:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

---

### 8. 通知模块 (Notification)

#### 8.1 获取客户收件箱

**接口地址**: `GET /customer/inbox`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 获取客户的所有通知消息

**响应示例**:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "customer_id": 1,
        "order_id": 3,
        "message": "您的订单 #3 已被服务商接受",
        "created_at": "2025-10-17T12:30:00",
        "is_read": false
      },
      {
        "customer_id": 1,
        "order_id": 3,
        "message": "订单 #3 已完成，请及时支付",
        "created_at": "2025-10-17T15:00:00",
        "is_read": false
      },
      {
        "customer_id": 1,
        "order_id": 3,
        "message": "订单 #3 支付成功",
        "created_at": "2025-10-17T15:10:00",
        "is_read": true
      }
    ],
    "total": 3
  },
  "message": "Success",
  "error": null
}
```

---

#### 8.2 获取服务商收件箱

**接口地址**: `GET /provider/inbox`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 获取服务商的所有通知消息

**响应示例**:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "provider_id": 2,
        "order_id": 3,
        "message": "您成功接受了订单 #3",
        "created_at": "2025-10-17T12:30:00",
        "is_read": true
      },
      {
        "provider_id": 2,
        "order_id": 3,
        "message": "订单 #3 已收到付款",
        "created_at": "2025-10-17T15:10:00",
        "is_read": false
      },
      {
        "provider_id": 2,
        "order_id": 3,
        "message": "客户对订单 #3 进行了评价（5星）",
        "created_at": "2025-10-17T15:20:00",
        "is_read": false
      }
    ],
    "total": 3
  },
  "message": "Success",
  "error": null
}
```

---

## 🔄 典型业务流程

### 流程 1: 客户发布并支付订单

```
1. 注册/登录 (POST /auth/register, POST /auth/login)
2. 创建客户资料 (POST /customer/profile)
3. 充值余额 (POST /customer/payments/recharge)
4. 发布订单 (POST /customer/orders/publish)
5. 等待服务商接单（查询订单状态 GET /customer/orders）
6. 订单完成后支付 (POST /customer/payments/pay)
7. 创建评价 (POST /reviews)
8. 查看通知 (GET /customer/inbox)
```

### 流程 2: 服务商接单并提供服务

```
1. 注册/登录 (POST /auth/register, POST /auth/login)
2. 创建服务商资料 (POST /provider/profile)
3. 查看可接单 (GET /provider/orders/available)
4. 接受订单 (POST /provider/orders/accept/{order_id})
5. 更新订单状态为进行中 (POST /provider/orders/status/{order_id})
6. 完成订单 (POST /provider/orders/status/{order_id})
7. 等待客户支付（查看通知 GET /provider/inbox）
8. 查看收到的评价 (GET /reviews/provider/me/reviews)
```

---

## ⚠️ 常见错误处理

### 错误 1: Token 过期

**错误响应**:
```json
{
  "detail": "Token has expired"
}
```

**解决方法**: 重新登录获取新的 Token

---

### 错误 2: 权限不足

**错误响应**:
```json
{
  "detail": "Insufficient permissions"
}
```

**解决方法**: 确认当前用户角色是否有权限访问该接口

---

### 错误 3: 余额不足

**错误响应**:
```json
{
  "success": false,
  "data": null,
  "message": "Insufficient balance",
  "error": "Your balance is not enough to complete this payment"
}
```

**解决方法**: 先充值再支付

---

### 错误 4: 订单状态不正确

**错误响应**:
```json
{
  "success": false,
  "data": null,
  "message": "Invalid order status",
  "error": "Order must be completed before payment"
}
```

**解决方法**: 检查订单当前状态，确认是否符合操作要求

---

## 🛡️ 安全建议

1. **保护 Token**: 不要在前端代码中硬编码 Token，使用安全的存储方式（如 HttpOnly Cookie 或加密的 LocalStorage）
2. **HTTPS**: 生产环境必须使用 HTTPS 协议
3. **输入验证**: 前端也应对用户输入进行基本验证
4. **错误处理**: 不要在前端展示详细的错误信息，以防泄露系统信息
5. **限流注意**: 注意接口调用频率，避免触发限流（60次/分钟）

---

## 📞 技术支持

如有任何问题，请联系后端开发团队。

**文档版本**: v1.0  
**最后更新**: 2025-10-17
