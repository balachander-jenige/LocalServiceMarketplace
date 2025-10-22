# 前端 API 文档更新说明 v1.1.1

## 📅 更新日期
2025-10-22

---

## 🎯 更新概览

本次更新（v1.1 → v1.1.1）主要解决了订单列表接口返回数据不完整的问题，并新增了订单详情查询接口。

---

## ✨ 主要变更

### 1. 订单列表接口返回完整字段

之前所有订单列表接口仅返回部分摘要信息（7个字段），现已更新为返回完整的订单详情（17个字段）。

#### 受影响的接口

| 接口 | 变更说明 |
|------|----------|
| `GET /customer/orders` | 返回类型从 OrderSummary 改为 OrderDetail |
| `GET /customer/orders/history` | 返回类型从 OrderSummary 改为 OrderDetail |
| `GET /provider/orders/available` | 返回类型从 OrderSummary 改为 OrderDetail |
| `GET /provider/orders/history` | 返回类型从 OrderSummary 改为 OrderDetail |
| `GET /admin/orders` | 返回类型从 OrderSummary 改为 OrderDetail |
| `GET /admin/orders/pending-review` | 返回类型从 OrderSummary 改为 OrderDetail |

#### 字段对比

**旧版本（OrderSummary - 7个字段）**:
```json
{
  "id": 1,
  "title": "家庭清洁服务",
  "service_type": "cleaning_repair",
  "status": "pending",
  "price": 200.0,
  "location": "NORTH",
  "created_at": "2025-10-17T10:00:00"
}
```

**新版本（OrderDetail - 17个字段）**:
```json
{
  "id": 1,
  "customer_id": 5,
  "title": "家庭清洁服务",
  "description": "需要对100平米的房屋进行深度清洁",
  "service_type": "cleaning_repair",
  "status": "pending",
  "price": 200.0,
  "location": "NORTH",
  "address": "123 Main Street, Apt 5",
  "service_start_time": "2025-10-25T09:00:00",
  "service_end_time": "2025-10-25T12:00:00",
  "created_at": "2025-10-17T10:00:00",
  "updated_at": "2025-10-17T11:00:00",
  "provider_id": 2,
  "payment_status": "pending"
}
```

#### 新增字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| customer_id | integer | 客户用户ID |
| description | string/null | 订单详细描述 |
| address | string/null | 详细地址 |
| service_start_time | string/null | 服务开始时间（ISO 8601格式）|
| service_end_time | string/null | 服务结束时间（ISO 8601格式）|
| updated_at | string | 订单最后更新时间 |
| provider_id | integer/null | 服务商用户ID（接单后才有值）|
| payment_status | string | 支付状态（pending/paid）|

---

### 2. 新增订单详情查询接口

为了方便前端查询单个订单的完整信息，新增了两个订单详情接口。

#### 2.1 客户订单详情

**接口**: `GET /customer/orders/my/{order_id}`  
**说明**: 客户查询自己订单的详细信息  
**认证**: 需要 Customer 角色

**示例**:
```
GET /customer/orders/my/1
```

**响应**:
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

#### 2.2 服务商订单详情

**接口**: `GET /provider/orders/my/{order_id}`  
**说明**: 服务商查询自己已接订单的详细信息  
**认证**: 需要 Provider 角色

**示例**:
```
GET /provider/orders/my/14
```

**响应**:
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

## 📋 完整字段列表

### OrderDetail（订单完整信息）

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| id | integer | 订单ID | 1 |
| customer_id | integer | 客户用户ID | 5 |
| title | string | 订单标题 | "家庭清洁服务" |
| description | string/null | 订单详细描述 | "需要对100平米的房屋进行深度清洁" |
| service_type | string | 服务类型 | "cleaning_repair" |
| status | string | 订单状态 | "pending" |
| price | number | 订单金额 | 200.0 |
| location | string | 服务地区 | "NORTH" |
| address | string/null | 详细地址 | "123 Main Street, Apt 5" |
| service_start_time | string/null | 服务开始时间 | "2025-10-25T09:00:00" |
| service_end_time | string/null | 服务结束时间 | "2025-10-25T12:00:00" |
| created_at | string | 创建时间 | "2025-10-17T10:00:00" |
| updated_at | string | 更新时间 | "2025-10-17T11:00:00" |
| provider_id | integer/null | 服务商ID | 2 或 null |
| payment_status | string | 支付状态 | "pending" 或 "paid" |

**共计**: 17个字段

---

## 🔄 前端适配建议

### 1. 响应数据结构变更

如果之前的前端代码假设订单列表只有7个字段，现在会收到17个字段。这是**向后兼容**的变更，旧字段仍然存在，只是新增了更多字段。

**建议**:
- 更新 TypeScript 接口定义或数据类型
- 利用新增字段优化UI展示（如显示描述、地址等）
- 可以直接使用列表数据，无需再单独查询详情

### 2. 新增接口使用场景

**客户端**:
- 订单详情页：使用 `GET /customer/orders/my/{order_id}`
- 订单卡片点击：直接显示列表数据（已包含完整信息）

**服务商端**:
- 订单详情页：使用 `GET /provider/orders/my/{order_id}`
- 可接单详情：直接使用 `GET /provider/orders/available` 的数据

### 3. TypeScript 接口示例

```typescript
// 订单完整信息
interface OrderDetail {
  id: number;
  customer_id: number;
  title: string;
  description: string | null;
  service_type: string;
  status: string;
  price: number;
  location: string;
  address: string | null;
  service_start_time: string | null;
  service_end_time: string | null;
  created_at: string;
  updated_at: string;
  provider_id: number | null;
  payment_status: string;
}

// API 响应
interface OrderListResponse {
  success: boolean;
  data: OrderDetail[];
  message: string;
  error: string | null;
}

interface OrderDetailResponse {
  success: boolean;
  data: OrderDetail;
  message: string;
  error: string | null;
}
```

---

## ⚠️ 破坏性变更

**无破坏性变更**！

本次更新是向后兼容的：
- ✅ 所有旧字段仍然存在
- ✅ 只是新增了更多字段
- ✅ 响应结构保持不变（仍然是数组或单个对象）
- ✅ HTTP 状态码和错误处理机制不变

---

## 🧪 测试建议

### 测试点

1. **订单列表接口**
   - 验证返回数据包含17个字段
   - 验证新增字段类型正确
   - 验证 null 值处理

2. **订单详情接口**
   - 验证路径参数正确
   - 验证权限控制（只能查看自己的订单）
   - 验证不存在的订单返回404

3. **数据一致性**
   - 验证列表和详情接口返回的数据一致
   - 验证时间格式为 ISO 8601

---

## 📞 技术支持

如有任何问题，请联系后端开发团队。

**文档版本**: v1.1.1  
**更新日期**: 2025-10-22
