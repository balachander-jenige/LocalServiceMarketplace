# Review Service 快速测试参考

## 🎯 核心端点

### Customer 端点
| 端点 | 方法 | 认证 | 功能 |
|------|------|------|------|
| `/reviews/` | POST | ✅ | 创建评价 |

### Provider 专用端点
| 端点 | 方法 | 认证 | 功能 |
|------|------|------|------|
| `/reviews/provider/me/rating` | GET | ✅ | 查看自己的评分 |
| `/reviews/provider/me/reviews` | GET | ✅ | 查看自己的所有评价 |

### 公开查询端点
| 端点 | 方法 | 认证 | 功能 |
|------|------|------|------|
| `/reviews/provider/{id}/rating` | GET | ❌ | 获取指定服务商评分 |
| `/reviews/provider/{id}` | GET | ❌ | 获取指定服务商所有评价 |
| `/reviews/order/{id}` | GET | ❌ | 获取订单评价 |

## 📋 测试快速流程（5分钟）

```bash
# 1. 健康检查
GET http://localhost:8005/health

# 2. 准备数据（使用已有的 customer 和 provider）
# - Customer token
# - Provider token  
# - 已完成并支付的订单 ID

# 3. 创建评价
POST http://localhost:8005/reviews/
Authorization: Bearer <customer_token>
{
  "order_id": 1,
  "stars": 5,
  "content": "Great!"
}
# ✅ 不需要 customer_id 和 provider_id，系统自动从订单获取

# 4. Provider 查看自己的评分 ⭐ 新增
GET http://localhost:8005/reviews/provider/me/rating
Authorization: Bearer <provider_token>
# 预期: average_rating=5.0, total_reviews=1

# 5. Provider 查看自己的评价列表 ⭐ 新增
GET http://localhost:8005/reviews/provider/me/reviews
Authorization: Bearer <provider_token>
# 预期: 返回包含刚创建评价的数组

# 6. 公开查询：根据订单查询
GET http://localhost:8005/reviews/order/1
# 预期: 返回订单的评价详情

# 7. 公开查询：服务商评分（需要知道 provider_id）
GET http://localhost:8005/reviews/provider/2/rating
# 预期: average_rating=5.0, total_reviews=1
```

## ⚠️ 关键验证点

### ✅ 必须通过的测试
1. **创建评价** - 返回 201，数据库有记录
2. **重复评价** - 返回 400 "already been reviewed"
3. **评价他人订单** - 返回 403 "only review your own orders"
4. **未完成订单** - 返回 400 "only review completed orders"
5. **未支付订单** - 返回 400 "only review paid orders"
6. **评分计算** - 多个评价后平均分正确
7. **未认证** - 返回 401

### 📊 平均分计算验证
```
评价1: 5星 → 平均 5.0, 总数 1
评价2: 3星 → 平均 4.0, 总数 2  // (5+3)/2
评价3: 1星 → 平均 3.0, 总数 3  // (5+3+1)/3
```

## 🔧 依赖服务检查

```bash
# 确保这些服务都在运行
lsof -i :8000  # Auth ✅
lsof -i :8002  # User ✅
lsof -i :8003  # Order ✅
lsof -i :8004  # Payment ✅
lsof -i :8005  # Review ⭐
```

## 🐛 快速排错

| 错误 | 原因 | 解决 |
|------|------|------|
| 401 | Token 无效 | 重新登录 |
| 403 | 评价他人订单 | 使用订单所属 customer 的 token |
| 400 | 订单已评价 | 创建新订单 |
| 400 | 订单未完成 | 等待订单完成 |
| 400 | 订单未支付 | 先支付订单 |
| 422 | stars 超出范围 | 使用 1-5 |
| 404 | 订单不存在 | 检查 order_id |

## 📝 最小测试数据

```json
// 创建评价最小请求（简化版）
{
  "order_id": 1,
  "stars": 5
}
// content 是可选的
// customer_id 和 provider_id 自动从订单获取
```

## 🎯 一次性测试脚本（Postman Pre-request）

```javascript
// 设置环境变量
pm.environment.set("review_url", "http://localhost:8005");

// 自动提取 token（在 Login 的 Tests 中）
pm.environment.set("customer_token", pm.response.json().access_token);

// 自动提取 user_id（在 /users/me 的 Tests 中）
pm.environment.set("customer_id", pm.response.json().id);

// 自动提取 order_id（在创建订单的 Tests 中）
pm.environment.set("order_id", pm.response.json().order_id);
```

## 完整测试指南
详见: `POSTMAN_TEST_GUIDE.md`
