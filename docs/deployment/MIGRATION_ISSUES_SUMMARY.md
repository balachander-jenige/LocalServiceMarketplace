# 微服务迁移问题总结

## Auth Service

### 数据库问题
- ❌ Alembic 迁移失败 - 未正确配置数据库连接
- ❌ MySQL 表结构与模型定义不匹配
- ✅ 需要手动执行 `alembic upgrade head`

### 依赖问题
- ❌ `passlib[bcrypt]` 缺失导致密码加密失败
- ❌ `python-jose[cryptography]` 缺失导致 JWT 生成失败
- ✅ 必须安装完整依赖: `poetry add passlib[bcrypt] python-jose[cryptography]`

### 配置问题
- ❌ `.env` 缺少 `SECRET_KEY` 和 `ALGORITHM`
- ❌ `DATABASE_URL` 格式错误
- ✅ 需要配置: `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`

---

## User Service

### 数据库连接问题
- ❌ MongoDB 连接字符串格式错误
- ❌ 未正确处理异步连接生命周期
- ✅ 使用 `motor` 驱动: `AsyncIOMotorClient`
- ✅ 在 `lifespan` 中管理连接

### 模型验证问题
- ❌ Pydantic 模型缺少默认值导致验证失败
- ❌ Enum 类型使用不当
- ✅ 使用 `Field(default=...)` 设置默认值

### 事件消费问题
- ❌ RabbitMQ 事件消费未正确启动
- ❌ 异步任务未用 `asyncio.create_task()`
- ✅ 在 `lifespan` 中启动消费: `asyncio.create_task(start_consuming())`

---

## Order Service

### 数据库迁移问题
- ❌ Alembic 自动生成迁移文件有误
- ❌ 枚举类型定义与数据库不一致
- ✅ 手动修改迁移文件确保类型匹配

### 跨服务调用问题
- ❌ 调用 User Service 时未传递 token
- ❌ 硬编码的 token 验证逻辑
- ✅ 使用 `get_current_user_id` 依赖项统一认证

### 状态管理问题
- ❌ 订单状态流转验证不完整
- ❌ 支付状态未正确初始化
- ✅ 添加状态机验证逻辑

---

## Payment Service

### 数据库驱动问题
- ❌ MySQL 数据库使用了 PostgreSQL 驱动 `asyncpg`
- ❌ 端口配置错误: 5432 → 应该是 3306
- ✅ 使用正确驱动: `mysql+aiomysql://...`

### 微服务认证问题
- ❌ 调用 Order/User Service 时缺少 Authorization header
- ❌ 传递错误的 token 值: `settings.AUTH_SERVICE_URL` 而非真实 token
- ✅ API 层获取 token → 传递给 Service 层 → 调用外部服务时使用

### 响应验证问题
- ❌ HTTP 调用未检查响应状态码
- ❌ 更新失败静默忽略，导致数据不一致
- ✅ 所有 HTTP 调用必须检查 `status_code` 并抛出异常

### 架构设计问题
- ❌ API 层和 Service 层职责不清
- ❌ Token 在 API 层获取但未传递到 Service 层
- ✅ 明确职责: API 层负责认证，Service 层负责业务逻辑

---

## 🎯 通用迁移检查清单

### 数据库配置 (所有服务)
- [ ] 确认数据库类型并使用正确驱动
  - MySQL → `aiomysql`
  - PostgreSQL → `asyncpg`
  - MongoDB → `motor`
- [ ] 验证连接字符串格式和端口
  - MySQL: 3306
  - PostgreSQL: 5432
  - MongoDB: 27017
- [ ] 添加 `greenlet` (SQLAlchemy async 必需)
- [ ] 执行数据库迁移 (`alembic upgrade head`)

### 认证与授权 (需要认证的服务)
- [ ] 实现 `get_current_user_id` 依赖项
- [ ] API 层使用 `HTTPAuthorizationCredentials` 获取 token
- [ ] Service 层接收 token 参数
- [ ] 跨服务调用时传递 `Authorization: Bearer {token}`
- [ ] **绝不**传递配置 URL 作为 token

### 跨服务通信 (调用其他服务的服务)
- [ ] 识别所有需要调用其他服务的地方
- [ ] 确保受保护端点传递 JWT token
- [ ] **检查所有 HTTP 响应状态码**
- [ ] 响应失败时抛出明确异常
- [ ] 包含详细错误信息: `response.text`

### 消息队列 (使用 RabbitMQ 的服务)
- [ ] 在 `lifespan` 中连接 RabbitMQ
- [ ] 使用 `asyncio.create_task()` 启动事件消费
- [ ] 正确处理消息确认/拒绝
- [ ] 实现事件发布/订阅逻辑

### 依赖管理 (所有服务)
- [ ] 安装所有必需依赖 (`poetry install`)
- [ ] 验证 Python 版本兼容性
- [ ] 特殊依赖注意完整安装: `passlib[bcrypt]`, `python-jose[cryptography]`

### 环境变量 (所有服务)
- [ ] 配置数据库连接
- [ ] 配置 RabbitMQ 连接 (如需要)
- [ ] 配置依赖服务 URL (AUTH/USER/ORDER)
- [ ] 配置服务端口
- [ ] 配置密钥和算法 (Auth Service)

### 测试验证 (所有服务)
- [ ] 健康检查端点返回 200
- [ ] 数据库连接成功
- [ ] 所有 API 端点可访问
- [ ] 跨服务调用成功
- [ ] 事件发布/订阅正常 (如有)
- [ ] 数据一致性验证

---

## 💡 最常见的 3 个错误

### 1️⃣ 数据库驱动与类型不匹配
```python
# ❌ 错误
DATABASE_URL=mysql+asyncpg://...  # MySQL 用了 PostgreSQL 驱动

# ✅ 正确
DATABASE_URL=mysql+aiomysql://...
```

### 2️⃣ 跨服务调用未传递 token
```python
# ❌ 错误
response = await client.get(f"{SERVICE_URL}/endpoint")

# ✅ 正确
response = await client.get(
    f"{SERVICE_URL}/endpoint",
    headers={"Authorization": f"Bearer {token}"}
)
```

### 3️⃣ 未检查 HTTP 响应状态
```python
# ❌ 错误
response = await client.put(url, json=data)
# 继续执行，即使失败

# ✅ 正确
response = await client.put(url, json=data)
if response.status_code != 200:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed: {response.text}"
    )
```

---

## 📌 记住：微服务迁移的核心是 **认证传递** 和 **错误处理**！
