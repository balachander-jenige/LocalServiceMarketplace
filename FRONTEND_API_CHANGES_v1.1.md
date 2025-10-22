# 前端 API 文档更新说明 (v1.0 → v1.1)

## 📅 更新日期
2025-10-21

---

## 🎯 主要变更概览

### 1. **新增管理员角色**
- 角色 ID: 3 (Admin)
- 职责: 审核订单、管理用户

### 2. **订单审核流程** ⭐ 重要变更
- 订单发布后状态为 `pending_review`（待审核）
- 需要管理员审核通过后才能被服务商接单
- 客户会在收件箱收到审核结果通知

### 3. **订单字段增强**
- 新增 `service_type` 字段（必填）
- 新增 `service_start_time` 字段（可选）
- 新增 `service_end_time` 字段（可选）

### 4. **支付系统简化** ⭐ 重要变更
- 移除充值功能（`POST /customer/payments/recharge`）
- 改为模拟支付，无需实际资金

### 5. **通知系统增强**
- 客户收件箱新增订单审核通过通知
- 客户收件箱新增订单审核拒绝通知（含拒绝原因）

### 6. **新增管理员 API 模块** ⭐ 重要变更
- 订单管理接口（6 个）: 查询、审核、编辑、删除订单
- 用户管理接口（4 个）: 查询、编辑、删除用户
- 详见主文档第 8 节: Admin Module

---

## 📝 详细变更说明

### 变更 1: 订单发布接口 (`POST /customer/orders/publish`)

#### 新增字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| service_type | string | ✅ | 服务类型（cleaning_repair/it_technology/education_training/life_health/design_consulting/other）|
| service_start_time | string | ❌ | 服务开始时间（ISO 8601格式）|
| service_end_time | string | ❌ | 服务结束时间（ISO 8601格式）|

#### 旧请求示例（v1.0）
```json
{
  "title": "家庭清洁服务",
  "description": "需要对100平米的房屋进行深度清洁",
  "price": 200.0,
  "location": "NORTH",
  "address": "123 Main Street, Apt 5"
}
```

#### 新请求示例（v1.1）
```json
{
  "title": "家庭清洁服务",
  "description": "需要对100平米的房屋进行深度清洁",
  "service_type": "cleaning_repair",          // 新增：必填
  "price": 200.0,
  "location": "NORTH",
  "address": "123 Main Street, Apt 5",
  "service_start_time": "2025-10-25T09:00:00",  // 新增：可选
  "service_end_time": "2025-10-25T12:00:00"     // 新增：可选
}
```

#### 响应变更

**旧响应（v1.0）**:
```json
{
  "success": true,
  "data": {
    "order_id": 1,
    "status": "pending",
    "message": "Order published successfully."
  }
}
```

**新响应（v1.1）**:
```json
{
  "success": true,
  "data": {
    "order_id": 1,
    "status": "pending_review",        // 状态变更
    "message": "Order published successfully. Waiting for admin approval."
  }
}
```

---

### 变更 2: 订单状态枚举

#### 新增状态

| 状态 | 说明 | 何时出现 |
|------|------|---------|
| pending_review | 待审核 | 订单刚发布时 |

#### 完整状态列表（v1.1）

| 状态 | 说明 | 可执行操作 |
|------|------|-----------|
| pending_review | 待审核 | 客户可取消 |
| pending | 待接单 | 服务商可接单，客户可取消 |
| accepted | 已接单 | 服务商可更新状态 |
| in_progress | 进行中 | 服务商可完成订单 |
| completed | 已完成 | 客户可支付 |
| cancelled | 已取消 | 无操作 |
| paid | 已支付 | 客户可评价 |

---

### 变更 3: 支付接口移除

#### ❌ 移除的接口

**接口**: `POST /customer/payments/recharge`  
**原用途**: 客户账户充值  
**移除原因**: 系统改为模拟支付，不需要实际资金流转

#### 旧流程（v1.0）
```
1. 充值余额 (POST /customer/payments/recharge)
2. 支付订单 (POST /customer/payments/pay)
```

#### 新流程（v1.1）
```
1. 直接支付订单 (POST /customer/payments/pay) - 模拟支付
```

#### 支付接口响应变更

**旧响应（v1.0）** - 包含余额信息:
```json
{
  "payment_id": 2,
  "order_id": 3,
  "balance": 250.0,              // ❌ 移除
  "message": "Payment successful."
}
```

**新响应（v1.1）** - 不包含余额信息:
```json
{
  "payment_id": 2,
  "order_id": 3,
  "message": "Payment successful."
}
```

---

### 变更 4: 通知系统增强

#### 新增通知类型

**1. 订单审核通过通知**
```json
{
  "customer_id": 1,
  "order_id": 5,
  "message": "Your order 5 has been approved by admin. It is now available for providers to accept.",
  "created_at": "2025-10-21T09:00:00",
  "is_read": false
}
```

**2. 订单审核拒绝通知**
```json
{
  "customer_id": 1,
  "order_id": 6,
  "message": "Your order 6 has been rejected by admin. Reason: 服务描述不清晰",
  "created_at": "2025-10-21T09:05:00",
  "is_read": false
}
```

#### 通知接口无变更
- 接口地址仍为 `GET /customer/inbox`
- 只是返回数据中会包含新类型的通知

---

## 🔄 前端适配建议

### 1. 订单发布表单

#### 需要添加的表单字段

```html
<!-- 服务类型选择（必填） -->
<select name="service_type" required>
  <option value="cleaning">清洁服务</option>
  <option value="repair">维修服务</option>
  <option value="moving">搬运服务</option>
  <option value="tutoring">辅导服务</option>
  <option value="delivery">配送服务</option>
  <option value="other">其他服务</option>
</select>

<!-- 服务时间选择（可选） -->
<input type="datetime-local" name="service_start_time">
<input type="datetime-local" name="service_end_time">
```

### 2. 订单状态显示

#### 状态徽章映射

```javascript
const statusMap = {
  'pending_review': {
    text: '待审核',
    color: 'orange',
    icon: 'clock'
  },
  'pending': {
    text: '待接单',
    color: 'blue',
    icon: 'search'
  },
  'accepted': {
    text: '已接单',
    color: 'green',
    icon: 'check'
  },
  // ... 其他状态
};
```

### 3. 订单列表过滤

#### 服务商端 - 可接单列表

```javascript
// 旧逻辑 (v1.0)
const availableOrders = orders.filter(o => o.status === 'pending');

// 新逻辑 (v1.1) - 无需修改，后端已过滤
// 只返回 status=pending 的订单
const availableOrders = await fetchAvailableOrders();
```

### 4. 移除充值功能

#### 需要删除的代码

```javascript
// ❌ 移除充值表单
<form onSubmit={handleRecharge}>
  <input type="number" name="amount" />
  <button>充值</button>
</form>

// ❌ 移除充值 API 调用
async function recharge(amount) {
  await api.post('/customer/payments/recharge', { amount });
}

// ❌ 移除余额显示（如果有）
<div>账户余额: {balance}</div>
```

#### 简化支付流程

```javascript
// 旧流程 (v1.0)
async function payOrder(orderId) {
  // 1. 检查余额
  const profile = await getCustomerProfile();
  if (profile.balance < orderPrice) {
    showRechargeDialog();
    return;
  }
  
  // 2. 支付
  await api.post('/customer/payments/pay', { order_id: orderId });
}

// 新流程 (v1.1)
async function payOrder(orderId) {
  // 直接支付，无需检查余额
  await api.post('/customer/payments/pay', { order_id: orderId });
}
```

### 5. 通知轮询增强

#### 建议在订单发布后轮询通知

```javascript
async function publishOrder(orderData) {
  const result = await api.post('/customer/orders/publish', orderData);
  
  if (result.data.status === 'pending_review') {
    // 显示等待审核提示
    showMessage('订单已提交，等待管理员审核...');
    
    // 开始轮询通知（建议每30秒）
    startNotificationPolling();
  }
}

function startNotificationPolling() {
  const pollInterval = setInterval(async () => {
    const inbox = await api.get('/customer/inbox');
    const unreadNotifications = inbox.data.items.filter(n => !n.is_read);
    
    // 检查是否有审核通知
    const approvalNotif = unreadNotifications.find(n => 
      n.message.includes('approved') || n.message.includes('rejected')
    );
    
    if (approvalNotif) {
      clearInterval(pollInterval);
      showNotification(approvalNotif.message);
      refreshOrders();
    }
  }, 30000); // 30秒轮询一次
}
```

---

## ⚠️ 破坏性变更

### 1. 充值接口移除 ⚠️

**影响**: 所有调用 `POST /customer/payments/recharge` 的代码会返回 404

**修复方法**: 删除所有充值相关的前端代码和 UI

### 2. 订单状态变更 ⚠️

**影响**: 
- 订单发布后状态不再是 `pending`，而是 `pending_review`
- 服务商只能看到 `pending` 状态的订单

**修复方法**: 
- 更新状态映射表
- 在客户端显示"等待审核"状态
- 服务商端无需修改（后端已过滤）

### 3. 订单发布必填字段增加 ⚠️

**影响**: 不提供 `service_type` 字段会导致请求失败

**修复方法**: 在订单发布表单中添加服务类型选择器

---

## 🧪 测试建议

### 测试场景 1: 订单发布与审核

```
1. 客户登录
2. 发布订单（包含 service_type）
3. 验证订单状态为 'pending_review'
4. 检查收件箱是否有发布成功通知
5. 等待管理员审核（或模拟审核）
6. 刷新收件箱，验证是否收到审核结果通知
7. 如果审核通过，验证订单状态变为 'pending'
```

### 测试场景 2: 模拟支付

```
1. 完成订单（status=completed）
2. 直接调用支付接口，无需检查余额
3. 验证支付成功
4. 验证订单状态变为 'paid'
```

### 测试场景 3: 服务商可接单列表

```
1. 服务商登录
2. 查看可接单列表
3. 验证列表中只有 'pending' 状态的订单
4. 验证没有 'pending_review' 状态的订单
```

---

## 📞 技术支持

如有疑问，请联系后端开发团队。

**文档版本**: v1.1  
**更新日期**: 2025-10-21
