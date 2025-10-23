# Admin 用户资料更新功能说明

## 概述

管理员现在可以通过一次 API 调用同时更新用户的基本信息（Auth Service）和 Profile 信息（User Service）。

## API 端点

```
PUT /admin/users/{user_id}
```

## 权限要求

- 需要管理员角色（role_id = 3）
- 请求头需包含有效的 JWT Token

## 请求体结构

### 基本用户字段（所有角色）

```json
{
  "username": "new_username",       // 可选：新用户名
  "email": "new@example.com",       // 可选：新邮箱
  "role_id": 2                      // 可选：新角色（1=customer, 2=provider, 3=admin）
}
```

### Customer Profile 字段（当用户为 Customer 时）

```json
{
  "location": "NORTH",               // 可选：区域（NORTH/SOUTH/EAST/WEST/MID）
  "address": "新地址",                // 可选：详细地址
  "budget_preference": 5000.0       // 可选：预算偏好
}
```

### Provider Profile 字段（当用户为 Provider 时）

```json
{
  "skills": ["Python", "React"],     // 可选：技能列表
  "experience_years": 5,             // 可选：工作年限
  "hourly_rate": 150.0,              // 可选：时薪
  "availability": "全职",             // 可选：可用性状态
  "portfolio": [                     // 可选：作品集链接
    "https://github.com/user",
    "https://example.com/portfolio"
  ]
}
```

## 使用示例

### 示例 1：更新 Customer 的用户名和地址

```bash
curl -X PUT http://localhost:8080/admin/users/123 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_customer_name",
    "location": "EAST",
    "address": "东城区新地址123号"
  }'
```

### 示例 2：更新 Provider 的邮箱和技能

```bash
curl -X PUT http://localhost:8080/admin/users/456 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "provider@newdomain.com",
    "skills": ["Vue.js", "Node.js", "MongoDB"],
    "hourly_rate": 200.0
  }'
```

### 示例 3：只更新用户基本信息

```bash
curl -X PUT http://localhost:8080/admin/users/789 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updated_username",
    "email": "updated@email.com"
  }'
```

### 示例 4：只更新 Profile 信息

```bash
curl -X PUT http://localhost:8080/admin/users/456 \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "experience_years": 8,
    "availability": "兼职"
  }'
```

## 响应格式

成功响应（200 OK）：

```json
{
  "user_id": 123,
  "username": "new_customer_name",
  "email": "customer@example.com",
  "role_id": 1,
  "role_name": "customer",
  "profile": {
    "user_id": 123,
    "location": "EAST",
    "address": "东城区新地址123号",
    "budget_preference": 5000.0,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 错误响应

### 404 Not Found - 用户不存在

```json
{
  "detail": "User not found"
}
```

### 403 Forbidden - 非管理员权限

```json
{
  "detail": "Admin access required"
}
```

### 500 Internal Server Error - 更新失败

```json
{
  "detail": "Failed to update user: error details"
}
```

## 注意事项

1. **字段选择性**：所有字段都是可选的，只需提供要更新的字段
2. **角色匹配**：
   - 当用户是 Customer（role_id=1）时，只有 Customer Profile 字段会被更新
   - 当用户是 Provider（role_id=2）时，只有 Provider Profile 字段会被更新
   - 当用户是 Admin（role_id=3）时，没有 Profile 需要更新
3. **Profile 不存在**：如果用户的 Profile 不存在，会记录警告但不影响基本信息更新
4. **原子性**：基本信息和 Profile 信息分别更新，基本信息更新失败会直接返回错误

## 实现逻辑

1. 更新 Auth Service 的用户字段（username, email, role_id）
2. 获取用户当前角色
3. 根据角色更新对应的 Profile：
   - role_id = 1 → 更新 Customer Profile
   - role_id = 2 → 更新 Provider Profile
   - role_id = 3 → 无 Profile 更新
4. 返回更新后的完整用户信息（包含 Profile）

## 相关服务

- **Gateway Service**: 端口 8080，路由请求并验证管理员权限
- **User Service**: 端口 8002，协调用户和 Profile 更新
- **Auth Service**: 端口 8000，处理用户基本信息更新

## 测试建议

1. 测试更新 Customer 的所有字段组合
2. 测试更新 Provider 的所有字段组合
3. 测试只更新基本信息（不提供 Profile 字段）
4. 测试只更新 Profile 信息（不提供基本字段）
5. 测试对不存在的用户进行更新
6. 测试非管理员用户调用该接口
