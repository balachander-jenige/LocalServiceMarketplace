# 前端接口文档 (Frontend API Documentation)

## 📋 文档说明

本文档为前端开发者提供完整的 API 接口说明，包括所有可用的接口、请求格式、响应格式和使用示例。

**版本**: v1.2  
**最后更新**: 2025-10-23  
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

系统支持三种用户角色：

| 角色 ID | 角色名称 | 说明 |
|---------|----------|------|
| 1 | Customer | 客户（发布订单、支付）|
| 2 | Provider | 服务商（接单、提供服务）|
| 3 | Admin | 管理员（审核订单、管理用户）|

---

## � 订单审核流程说明

订单发布后需要经过管理员审核才能被服务商接单：

### 订单生命周期

```
1. Customer 发布订单
   ↓
2. 订单状态: pending_review（待审核）
   ↓
3. 管理员审核
   ├─ 审核通过 → 状态变为 pending（待接单）
   │              Customer 收到通知："Your order has been approved..."
   │              订单出现在服务商的可接单列表中
   │
   └─ 审核拒绝 → 状态变为 cancelled（已取消）
                  Customer 收到通知："Your order has been rejected. Reason: ..."
                  订单结束
   ↓
4. Provider 接单（状态: accepted）
   ↓
5. 服务进行中（状态: in_progress）
   ↓
6. 服务完成（状态: completed）
   ↓
7. Customer 支付（状态: paid）
   ↓
8. Customer 评价（状态: pending_review）
```

### 重要提示

- **客户端**: 发布订单后需要轮询收件箱或订单状态，以获取审核结果
- **服务商端**: 只能看到审核通过（`status=pending`）的订单
- **审核时间**: 取决于管理员处理速度，建议在前端显示"等待审核"提示

---

## �📚 接口列表

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
**接口说明**: 客户发布新的服务订单。订单发布后状态为 `pending_review`，需要等待管理员审核通过后才能被服务商接单。

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | ✅ | 订单标题（不能为空）|
| description | string | ❌ | 订单详细描述 |
| service_type | string | ✅ | 服务类型（见下方可选值）|
| price | number | ✅ | 订单金额（必须>0）|
| location | string | ✅ | 服务地点 |
| address | string | ❌ | 详细地址 |
| service_start_time | string | ❌ | 服务开始时间（ISO 8601格式）|
| service_end_time | string | ❌ | 服务结束时间（ISO 8601格式）|

**service_type 可选值**:
- `cleaning_repair` - 清洁与维修
- `it_technology` - IT与技术
- `education_training` - 教育与培训
- `life_health` - 生活与健康
- `design_consulting` - 设计与咨询
- `other` - 其他服务

**请求示例**:

```json
{
  "title": "家庭清洁服务",
  "description": "需要对100平米的房屋进行深度清洁",
  "service_type": "cleaning_repair",
  "price": 200.0,
  "location": "NORTH",
  "address": "123 Main Street, Apt 5",
  "service_start_time": "2025-10-25T09:00:00",
  "service_end_time": "2025-10-25T12:00:00"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "order_id": 1,
    "status": "pending_review",
    "message": "Order published successfully. Waiting for admin approval."
  },
  "message": "Order published",
  "error": null
}
```

**重要提示**:
- 订单发布后状态为 `pending_review`（待审核）
- 需要等待管理员审核通过后，状态才会变为 `pending`（待接单）
- 客户会在收件箱收到审核结果通知
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
| pending_review | 待审核（管理员审核中）|
| pending | 待接单（审核通过，等待服务商接单）|
| accepted | 已接单（服务商已接单）|
| in_progress | 进行中 |
| completed | 已完成 |
| cancelled | 已取消 |
| paid | 已支付 |

---

#### 4.3 获取订单详情

**接口地址**: `GET /customer/orders/my/{order_id}`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 获取指定订单的详细信息

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求示例**:

```
GET /customer/orders/my/1
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "customer_id": 1,
    "title": "家庭清洁服务",
    "description": "需要对100平米的房屋进行深度清洁",
    "service_type": "cleaning_repair",
    "status": "accepted",
    "price": 200.0,
    "location": "NORTH",
    "address": "123 Main Street, Apt 5",
    "service_start_time": "2025-10-25T09:00:00",
    "service_end_time": "2025-10-25T12:00:00",
    "created_at": "2025-10-17T10:00:00",
    "updated_at": "2025-10-17T11:00:00",
    "provider_id": 2,
    "payment_status": "pending"
  },
  "message": "Success",
  "error": null
}
```

---
#### 4.4 获取订单历史

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

#### 4.5 取消订单

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
**接口说明**: 获取当前可以接的订单列表（状态为 pending 的订单），支持按地点、服务类型、价格范围和关键词筛选

**查询参数**（所有参数都是可选的）:

| 参数名 | 类型 | 必填 | 说明 | 可选值 |
|--------|------|------|------|--------|
| location | string | ❌ | 按地点筛选 | `NORTH`, `SOUTH`, `EAST`, `WEST`, `MID` |
| service_type | string | ❌ | 按服务类型筛选 | `cleaning_repair`, `it_technology`, `education_training`, `life_health`, `design_consulting`, `other` |
| min_price | number | ❌ | 最低价格筛选 | ≥ 0 |
| max_price | number | ❌ | 最高价格筛选 | ≥ 0 |
| keyword | string | ❌ | 关键词搜索（标题或描述）| 任意文本 |

**请求示例**:

```
# 不使用筛选，获取所有可接单
GET /provider/orders/available

# 按地点筛选
GET /provider/orders/available?location=EAST

# 按服务类型筛选
GET /provider/orders/available?service_type=cleaning_repair

# 同时按地点和服务类型筛选
GET /provider/orders/available?location=EAST&service_type=it_technology

# 组合多个筛选条件
GET /provider/orders/available?location=NORTH&service_type=life_health&min_price=100&max_price=500

# 关键词搜索 + 筛选
GET /provider/orders/available?keyword=维修&location=EAST
```

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

#### 5.2 获取可接单详情

**接口地址**: `GET /provider/orders/available/{order_id}`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 获取单个可接订单的详细信息（用于服务商查看订单详情后决定是否接单）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求示例**:

```
GET /provider/orders/available/3
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 3,
    "title": "家电维修",
    "description": "需要维修冰箱，不制冷",
    "status": "pending",
    "price": 250.0,
    "location": "EAST",
    "customer_id": 1,
    "provider_id": null,
    "created_at": "2025-10-17T12:00:00",
    "updated_at": "2025-10-17T12:00:00",
    "started_at": null,
    "completed_at": null,
    "cancelled_at": null
  },
  "message": "Order details retrieved successfully",
  "error": null
}
```

**错误响应示例**:

```json
{
  "success": false,
  "data": null,
  "message": "Order not found or not available",
  "error": "Order 999 does not exist or is not in pending status"
}
```

**注意事项**:
- 只能查看状态为 `pending` 的订单详情
- 如果订单不存在或状态不是 `pending`，将返回 404 错误
- 该接口返回订单的完整详情，方便服务商决定是否接单

---

#### 5.3 接受订单

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

#### 5.4 更新订单状态

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

#### 5.5 获取已接单订单详情

**接口地址**: `GET /provider/orders/my/{order_id}`  
**认证要求**: ✅ 需要认证（Provider 角色）  
**接口说明**: 获取服务商已接订单的详细信息

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求示例**:

```
GET /provider/orders/my/14
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 14,
    "customer_id": 5,
    "title": "家电维修",
    "description": "冰箱不制冷",
    "service_type": "cleaning_repair",
    "status": "accepted",
    "price": 250.0,
    "location": "EAST",
    "address": "789 Pine Street",
    "service_start_time": "2025-10-18T14:00:00",
    "service_end_time": "2025-10-18T16:00:00",
    "created_at": "2025-10-17T12:00:00",
    "updated_at": "2025-10-17T13:00:00",
    "provider_id": 2,
    "payment_status": "pending"
  },
  "message": "Success",
  "error": null
}
```

---

#### 5.6 获取订单历史

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

#### 6.1 支付订单

**接口地址**: `POST /customer/payments/pay`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 客户支付订单费用（使用模拟支付）

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
    "message": "Payment successful."
  },
  "message": "Payment successful",
  "error": null
}
```

**注意事项**:
- 系统使用模拟支付，无需实际资金
- 只能支付状态为 `completed` 的订单
- 支付成功后订单状态会变为 `paid`
- 支付成功后服务商会收到付款通知

---

### 7. 评价模块 (Review)

#### 7.1 创建评价

**接口地址**: `POST /reviews`  
**认证要求**: ✅ 需要认证（Customer 角色）  
**接口说明**: 客户对已完成并已支付的订单进行评价

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

### 8. 管理员模块 (Admin)

#### 8.1 获取所有订单

**接口地址**: `GET /admin/orders`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员获取所有订单，可按状态过滤

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | ❌ | 订单状态（pending_review/pending/accepted/in_progress/completed/cancelled/paid）|

**请求示例**:

```
GET /admin/orders?status=pending_review
```

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "家庭清洁服务",
      "customer_id": 5,
      "status": "pending_review",
      "service_type": "cleaning_repair",
      "price": 200.0,
      "location": "NORTH",
      "created_at": "2025-10-21T10:00:00"
    },
    {
      "id": 2,
      "title": "IT技术支持",
      "customer_id": 8,
      "status": "pending_review",
      "service_type": "it_technology",
      "price": 300.0,
      "location": "EAST",
      "created_at": "2025-10-21T11:00:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

---

#### 8.2 获取待审核订单列表

**接口地址**: `GET /admin/orders/pending-review`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员获取所有待审核的订单（status=pending_review）

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "家庭清洁服务",
      "customer_id": 5,
      "status": "pending_review",
      "service_type": "cleaning_repair",
      "price": 200.0,
      "location": "NORTH",
      "description": "需要对100平米的房屋进行深度清洁",
      "created_at": "2025-10-21T10:00:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

---

#### 8.3 获取订单详情

**接口地址**: `GET /admin/orders/{order_id}`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员获取指定订单的详细信息

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求示例**:

```
GET /admin/orders/1
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "家庭清洁服务",
    "description": "需要对100平米的房屋进行深度清洁",
    "customer_id": 5,
    "provider_id": null,
    "status": "pending_review",
    "service_type": "cleaning_repair",
    "price": 200.0,
    "location": "NORTH",
    "address": "123 Main Street, Apt 5",
    "service_start_time": "2025-10-25T09:00:00",
    "service_end_time": "2025-10-25T12:00:00",
    "created_at": "2025-10-21T10:00:00",
    "updated_at": "2025-10-21T10:00:00"
  },
  "message": "Success",
  "error": null
}
```

---

#### 8.4 审批订单

**接口地址**: `POST /admin/orders/{order_id}/approve`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员审批订单（批准或拒绝）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| approved | boolean | ✅ | 是否批准（true=批准，false=拒绝）|
| reject_reason | string | ❌ | 拒绝原因（拒绝时必填）|

**请求示例 - 批准**:

```json
{
  "approved": true
}
```

**请求示例 - 拒绝**:

```json
{
  "approved": false,
  "reject_reason": "服务描述不够详细，请补充具体要求"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "order_id": 1,
    "status": "pending",
    "message": "Order approved successfully"
  },
  "message": "Order approval processed",
  "error": null
}
```

**重要提示**:
- 批准后订单状态变为 `pending`（待接单）
- 拒绝后订单状态变为 `cancelled`（已取消）
- 客户会在收件箱收到审核结果通知

---

#### 8.5 更新订单信息

**接口地址**: `PUT /admin/orders/{order_id}`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员更新订单信息（所有字段可选）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| title | string | ❌ | 订单标题 |
| description | string | ❌ | 订单描述 |
| price | number | ❌ | 订单金额 |
| location | string | ❌ | 服务地点 |

**请求示例**:

```json
{
  "price": 250.0,
  "description": "需要对100平米的房屋进行深度清洁，包括厨房和卫生间"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "order_id": 1,
    "message": "Order updated successfully"
  },
  "message": "Order updated",
  "error": null
}
```

---

#### 8.6 删除订单

**接口地址**: `DELETE /admin/orders/{order_id}`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员删除订单

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| order_id | integer | ✅ | 订单 ID |

**请求示例**:

```
DELETE /admin/orders/1
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "order_id": 1,
    "message": "Order deleted successfully"
  },
  "message": "Order deleted",
  "error": null
}
```

---

#### 8.7 获取所有用户

**接口地址**: `GET /admin/users`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员获取所有用户列表，可按角色过滤

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| role_id | integer | ❌ | 角色 ID（1=Customer, 2=Provider, 3=Admin）|

**请求示例**:

```
GET /admin/users?role_id=1
```

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "user_id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "role_id": 1,
      "role_name": "customer",
      "has_profile": true,
      "created_at": "2025-10-15T10:00:00"
    },
    {
      "user_id": 5,
      "username": "jane_smith",
      "email": "jane@example.com",
      "role_id": 1,
      "role_name": "customer",
      "has_profile": true,
      "created_at": "2025-10-16T14:00:00"
    }
  ],
  "message": "Success",
  "error": null
}
```

---

#### 8.8 获取用户详情

**接口地址**: `GET /admin/users/{user_id}`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员获取指定用户的详细信息（包含 Profile）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | ✅ | 用户 ID |

**请求示例**:

```
GET /admin/users/1
```

**响应示例 - Customer**:

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role_id": 1,
    "role_name": "customer",
    "profile": {
      "user_id": 1,
      "location": "NORTH",
      "address": "123 Main Street",
      "budget_preference": 1000.0,
      "created_at": "2025-10-15T10:00:00",
      "updated_at": "2025-10-15T10:00:00"
    },
    "created_at": "2025-10-15T10:00:00"
  },
  "message": "Success",
  "error": null
}
```

---

#### 8.9 更新用户信息

**接口地址**: `PUT /admin/users/{user_id}`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员更新用户信息和 Profile（所有字段可选）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | ✅ | 用户 ID |

**请求参数**:

**基本用户字段**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | ❌ | 用户名 |
| email | string | ❌ | 邮箱 |
| role_id | integer | ❌ | 角色 ID |

**Customer Profile 字段**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| location | string | ❌ | 所在地区 |
| address | string | ❌ | 详细地址 |
| budget_preference | number | ❌ | 预算偏好 |

**Provider Profile 字段**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skills | array[string] | ❌ | 技能列表 |
| experience_years | integer | ❌ | 从业年限 |
| hourly_rate | number | ❌ | 时薪 |
| availability | string | ❌ | 可用时间 |
| portfolio | array[string] | ❌ | 作品集链接 |

**请求示例 - 更新 Customer**:

```json
{
  "username": "john_updated",
  "location": "SOUTH",
  "budget_preference": 2000.0
}
```

**请求示例 - 更新 Provider**:

```json
{
  "email": "newemail@example.com",
  "hourly_rate": 80.0,
  "skills": ["Python", "Java", "React"]
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "username": "john_updated",
    "email": "john@example.com",
    "role_id": 1,
    "role_name": "customer",
    "profile": {
      "user_id": 1,
      "location": "SOUTH",
      "address": "123 Main Street",
      "budget_preference": 2000.0,
      "created_at": "2025-10-15T10:00:00",
      "updated_at": "2025-10-21T15:00:00"
    },
    "created_at": "2025-10-15T10:00:00"
  },
  "message": "User updated",
  "error": null
}
```

---

#### 8.10 删除用户

**接口地址**: `DELETE /admin/users/{user_id}`  
**认证要求**: ✅ 需要认证（Admin 角色）  
**接口说明**: 管理员删除用户（同时删除用户的 Profile）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | ✅ | 用户 ID |

**请求示例**:

```
DELETE /admin/users/10
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 10,
    "message": "User deleted successfully"
  },
  "message": "User deleted",
  "error": null
}
```

---

### 9. 通知模块 (Notification)

#### 9.1 获取客户收件箱

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
        "order_id": 5,
        "message": "Your order 5 has been approved by admin. It is now available for providers to accept.",
        "created_at": "2025-10-21T09:00:00",
        "is_read": false
      },
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
    "total": 4
  },
  "message": "Success",
  "error": null
}
```

**通知类型说明**:
- **订单审核通过**: "Your order {order_id} has been approved by admin..."
- **订单审核拒绝**: "Your order {order_id} has been rejected by admin. Reason: {reason}"
- **订单被接受**: "您的订单 #{order_id} 已被服务商接受"
- **订单完成**: "订单 #{order_id} 已完成，请及时支付"
- **支付成功**: "订单 #{order_id} 支付成功"
```

---

#### 9.2 获取服务商收件箱

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
3. 发布订单 (POST /customer/orders/publish)
   - 订单状态: pending_review（待审核）
4. 等待管理员审核
   - 查看收件箱 (GET /customer/inbox) 获取审核结果
   - 审核通过: 订单状态变为 pending（待接单）
   - 审核拒绝: 订单状态变为 cancelled
5. 等待服务商接单（查询订单状态 GET /customer/orders）
6. 订单完成后支付 (POST /customer/payments/pay)
   - 使用模拟支付，无需充值
7. 创建评价 (POST /reviews)
8. 查看通知 (GET /customer/inbox)
```

### 流程 2: 服务商接单并提供服务

```
1. 注册/登录 (POST /auth/register, POST /auth/login)
2. 创建服务商资料 (POST /provider/profile)
3. 查看可接单列表 (GET /provider/orders/available)
   - 只显示审核通过（status=pending）的订单
4. 查看订单详情 (GET /provider/orders/available/{order_id})
   - 查看订单的完整信息以决定是否接单
5. 接受订单 (POST /provider/orders/accept/{order_id})
6. 更新订单状态为进行中 (POST /provider/orders/status/{order_id})
7. 完成订单 (POST /provider/orders/status/{order_id})
8. 等待客户支付（查看通知 GET /provider/inbox）
9. 查看收到的评价 (GET /reviews/provider/me/reviews)
```

### 流程 3: 管理员审核订单

```
1. 登录管理员账号 (POST /auth/login, role_id=3)
2. 查看待审核订单列表 (GET /admin/orders/pending-review)
3. 查看订单详情 (GET /admin/orders/{order_id})
4. 审批订单 (POST /admin/orders/{order_id}/approve)
   - 批准: approved=true → 订单状态变为 pending
   - 拒绝: approved=false + reject_reason → 订单状态变为 cancelled
5. 客户收到审核结果通知
```

### 流程 4: 管理员管理用户

```
1. 登录管理员账号 (POST /auth/login, role_id=3)
2. 查看所有用户 (GET /admin/users?role_id=1)
3. 查看用户详情 (GET /admin/users/{user_id})
4. 更新用户信息和 Profile (PUT /admin/users/{user_id})
5. 删除用户（如需要）(DELETE /admin/users/{user_id})
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

### 错误 3: 订单状态不正确

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

### 错误 4: 订单待审核

**错误响应**:
```json
{
  "success": false,
  "data": null,
  "message": "Order is pending review",
  "error": "Order is waiting for admin approval"
}
```

**解决方法**: 等待管理员审核通过后再进行操作

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

**文档版本**: v1.1  
**最后更新**: 2025-10-23

---

## 📝 版本更新日志

### v1.2 (2025-10-23)
- ✅ 新增服务商查看可接单详情接口 `GET /provider/orders/available/{order_id}`
- ✅ 服务商可以在接单前查看订单的完整详情信息
- ✅ 更新服务商接单流程，增加查看详情步骤
- ✅ 可接单列表接口支持按地点（`location`）和服务类型（`service_type`）筛选
- ✅ 可接单列表接口支持按价格范围（`min_price`/`max_price`）和关键词（`keyword`）筛选
- ✅ 所有筛选参数都是可选的，可以单独使用或组合使用

### v1.1 (2025-10-21)
- ✅ 新增管理员角色（role_id = 3）
- ✅ 新增管理员订单管理接口（查看/审核/更新/删除订单）
- ✅ 新增管理员用户管理接口（查看/更新/删除用户和 Profile）
- ✅ 订单发布后需要管理员审核（新增 `pending_review` 状态）
- ✅ 订单添加服务类型字段（`service_type`）- 修正为实际枚举值
- ✅ 订单添加服务时间字段（`service_start_time`, `service_end_time`）
- ✅ 客户收件箱新增审核通过/拒绝通知
- ✅ 支付系统简化为模拟支付（移除充值功能）
- ✅ 更新订单状态流程说明

### v1.0 (2025-10-17)
- 初始版本发布