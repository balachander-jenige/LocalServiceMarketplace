# User Service 单元测试文档

## 📋 概述

本文档详细说明 User Service 的单元测试实现、运行方式和覆盖范围。

## 🎯 测试目标

- **CustomerProfileService**: 客户资料的创建、查询、更新逻辑
- **ProviderProfileService**: 服务商资料的创建、查询、更新、搜索逻辑
- **AdminUserService**: 管理员用户管理逻辑(包含HTTP调用)

## 📊 测试统计

| 服务模块 | 测试类数量 | 测试用例数 | 覆盖率 | 状态 |
|---------|----------|-----------|--------|------|
| **Service层** | | | | |
| CustomerProfileService | 3 | 11 | 100% | ✅ |
| ProviderProfileService | 4 | 18 | 100% | ✅ |
| AdminUserService | 2 | 8 | 39% | ✅ |
| **DAO层** | | | | |
| CustomerProfileDAO | 4 | 10 | 100% | ✅ |
| ProviderProfileDAO | 5 | 17 | 100% | ✅ |
| **Core层** | | | | |
| Settings (Config) | 1 | 10 | 100% | ✅ |
| **总计** | **19** | **71** | **~50%** | **✅ 全部通过** |

## 🏗️ 测试架构

### 目录结构

```
src/user_service/tests/unit/
├── conftest.py                         # 共享Fixtures
├── __init__.py
├── test_core/                          # Core层测试
│   ├── __init__.py
│   └── test_config.py                  # 配置测试 (10个)
├── test_dao/                           # DAO层测试
│   ├── __init__.py
│   ├── test_customer_profile_dao.py   # CustomerDAO测试 (10个)
│   └── test_provider_profile_dao.py   # ProviderDAO测试 (17个)
└── test_services/                      # Service层测试
    ├── __init__.py
    ├── test_customer_profile_service.py    # 客户服务测试 (11个)
    ├── test_provider_profile_service.py    # 服务商服务测试 (18个)
    └── test_admin_user_service.py          # 管理员服务测试 (8个)
```

### Mock策略

| 依赖类型 | Mock方式 | 说明 |
|---------|---------|------|
| MongoDB | `MagicMock(AsyncIOMotorDatabase)` | 模拟Motor异步数据库 |
| EventPublisher | `AsyncMock()` | 模拟RabbitMQ事件发布 |
| httpx.AsyncClient | `AsyncMock()` | 模拟HTTP调用(Auth Service) |
| DAO层 | `mocker.patch.object()` | 单独Mock数据访问层 |

## 🧪 测试用例详解

### 1. Core层测试 (10个)

#### test_config.py - Settings配置测试
```python
✅ test_settings_with_env_vars - 从环境变量加载配置
✅ test_settings_default_values - 验证默认值设置
✅ test_settings_required_fields - 验证必需字段正确设置
✅ test_settings_mongodb_url_validation - MongoDB URL格式验证
✅ test_settings_rabbitmq_url_validation - RabbitMQ URL格式验证
✅ test_settings_service_port_type - 端口号类型转换
✅ test_settings_auth_service_url_override - Auth服务URL覆盖
✅ test_settings_log_level_values - 日志级别配置
✅ test_settings_service_name_custom - 自定义服务名
✅ test_settings_immutable - 配置对象不可变性
```

**测试重点**:
- 🔹 环境变量加载和优先级
- 🔹 默认值和类型转换
- 🔹 URL拼接和格式验证
- 🔹 配置对象完整性

---

### 2. DAO层测试 (27个)

#### test_customer_profile_dao.py - 客户档案DAO测试 (10个)

**创建操作 (3个)**:
```python
✅ test_create_success - 成功插入文档到MongoDB
✅ test_create_mongodb_error - 数据库异常处理
✅ test_create_removes_id_field - 自动移除_id字段避免冲突
```

**查询操作 (3个)**:
```python
✅ test_get_by_id_found - 按ObjectId查询返回Profile对象
✅ test_get_by_id_not_found - 查询不存在返回None
✅ test_get_by_user_id_success - 按user_id查询客户档案
```

**更新操作 (2个)**:
```python
✅ test_update_success - 更新成功返回更新后文档
✅ test_update_not_found - 更新不存在文档返回None
```

**删除操作 (2个)**:
```python
✅ test_delete_success - 删除成功返回True
✅ test_delete_not_found - 删除不存在返回False
```

#### test_provider_profile_dao.py - 服务商档案DAO测试 (17个)

**创建操作 (3个)**:
```python
✅ test_create_success - 成功插入服务商文档
✅ test_create_mongodb_error - 数据库异常处理
✅ test_create_removes_id_field - 自动移除_id字段
```

**查询操作 (3个)**:
```python
✅ test_get_by_id_found - 按ObjectId查询服务商档案
✅ test_get_by_id_not_found - 查询不存在返回None
✅ test_get_by_user_id_success - 按user_id查询服务商
```

**更新操作 (2个)**:
```python
✅ test_update_success - 更新成功返回更新后文档
✅ test_update_not_found - 更新不存在文档返回None
```

**删除操作 (2个)**:
```python
✅ test_delete_success - 删除成功返回True
✅ test_delete_not_found - 删除不存在返回False
```

**高级搜索 (7个)** 🌟:
```python
✅ test_search_by_category - 按服务类别精确匹配
✅ test_search_by_skills - 按技能数组包含查询($in操作符)
✅ test_search_by_hourly_rate_range - 按时薪范围过滤($gte/$lte)
✅ test_search_by_rating_min - 按最低评分过滤($gte)
✅ test_search_multiple_conditions - 多条件组合查询(AND逻辑)
✅ test_search_pagination - 分页和排序(按rating降序)
✅ test_search_empty_result - 空结果返回空列表
```

**DAO层测试重点**:
- 🔹 MongoDB CRUD操作正确性
- 🔹 ObjectId与string ID转换
- 🔹 _id字段处理避免冲突
- 🔹 复杂聚合查询(搜索功能)
- 🔹 异常处理和边界情况

---

### 3. Service层测试 (34个)

#### test_customer_profile_service.py - 客户档案服务测试 (11个)

**创建档案 (4个)**:
```python
✅ test_create_profile_success - 创建成功并发布CustomerCreatedEvent
✅ test_create_profile_already_exists - 用户已存在返回400错误
✅ test_create_profile_with_minimal_data - 最小必填字段创建
✅ test_create_profile_publishes_event - 验证事件发布到RabbitMQ
```

**查询档案 (2个)**:
```python
✅ test_get_profile_success - 按ID查询成功返回档案
✅ test_get_profile_not_found - 查询不存在返回404错误
```

**更新档案 (5个)**:
```python
✅ test_update_profile_success - 更新成功并发布CustomerUpdatedEvent
✅ test_update_profile_not_found - 更新不存在档案返回404
✅ test_update_profile_empty_data - 空数据验证返回400
✅ test_update_profile_filters_none_values - 自动过滤None值
✅ test_update_profile_publishes_event - 验证事件发布
```

#### test_provider_profile_service.py - 服务商档案服务测试 (18个)

**创建档案 (4个)**:
```python
✅ test_create_profile_success - 创建服务商并发布ProviderCreatedEvent
✅ test_create_profile_already_exists - 服务商已存在返回400
✅ test_create_profile_with_defaults - 验证默认值设置(rating=0.0)
✅ test_create_profile_publishes_event - 事件发布验证
```

**查询档案 (2个)**:
```python
✅ test_get_profile_success - 按ID查询服务商档案
✅ test_get_profile_not_found - 查询不存在返回404
```

**更新档案 (5个)**:
```python
✅ test_update_profile_success - 更新成功并发布ProviderUpdatedEvent
✅ test_update_profile_not_found - 更新不存在返回404
✅ test_update_profile_empty_data - 空数据验证返回400
✅ test_update_profile_filters_none_values - 自动过滤None值
✅ test_update_profile_publishes_event - 事件发布验证
```

**搜索功能 (7个)**:
```python
✅ test_search_by_category - 按类别搜索服务商
✅ test_search_by_skills - 按技能数组搜索
✅ test_search_by_hourly_rate - 按时薪范围搜索
✅ test_search_by_rating - 按最低评分搜索
✅ test_search_multiple_filters - 多条件组合搜索
✅ test_search_with_pagination - 分页和排序测试
✅ test_search_empty_results - 空结果处理
```

#### test_admin_user_service.py - 管理员服务测试 (8个)

**创建管理员 (3个)**:
```python
✅ test_create_admin_success - 通过Auth服务创建管理员
✅ test_create_admin_auth_service_error - Auth服务异常处理
✅ test_create_admin_event_publish_error - 事件发布失败(静默)
```

**查询管理员 (2个)**:
```python
✅ test_get_admin_success - 从Auth服务查询管理员信息
✅ test_get_admin_not_found - 管理员不存在返回404
```

**列表查询 (3个)**:
```python
✅ test_list_admins_success - 分页查询管理员列表
✅ test_list_admins_empty - 空列表处理
✅ test_list_admins_auth_service_error - Auth服务异常处理
```

**Service层测试重点**:
- 🔹 业务逻辑正确性
- 🔹 事件驱动架构(RabbitMQ事件发布)
- 🔹 HTTP客户端Mock(跨服务调用)
- 🔹 异常处理和错误码
- 🔹 数据验证和过滤

---

## 🛠️ Mock策略说明

### 1. 数据库Mock (MongoDB)

**DAO层测试**:
```python
@pytest.fixture
def mock_mongo_db(mocker):
    mock_db = mocker.MagicMock()
    mock_collection = mocker.AsyncMock()
    mock_db.__getitem__.return_value = mock_collection
    return mock_db
```
- 使用 `AsyncMock` 模拟MongoDB Motor异步操作
- Mock `insert_one`, `find_one`, `update_one`, `delete_one`
- Mock聚合查询: `cursor.limit().to_list()`

**Service层测试**:
- 直接Mock DAO对象,不依赖真实数据库
- 使用 `mocker.patch.object()` 替换DAO方法

### 2. 消息队列Mock (RabbitMQ)

```python
@pytest.fixture
def mock_event_publisher(mocker):
    mock_publisher = mocker.AsyncMock()
    mock_publisher.publish_event = mocker.AsyncMock()
    return mock_publisher
```
- Mock `EventPublisher.publish_event()` 方法
- 验证事件发布但不真实连接RabbitMQ
- 使用 `assert_called_once_with()` 验证事件内容

### 3. HTTP客户端Mock (跨服务调用)

```python
@pytest.fixture
def mock_httpx_client(mocker):
    mock_client = mocker.AsyncMock()
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"user_id": 1, "role": "admin"}
    mock_client.get.return_value = mock_response
    return mock_client
```
- Mock `httpx.AsyncClient` 异步HTTP调用
- 模拟Auth Service的API响应
- 支持状态码和JSON响应Mock

### 4. 环境变量Mock

```python
with patch.dict(os.environ, {
    "MONGODB_HOST": "test-mongo",
    "MONGODB_PORT": "27017",
    "RABBITMQ_USER": "testuser"
}):
    settings = Settings()
```
- 使用 `patch.dict(os.environ)` 临时修改环境变量
- 测试配置加载逻辑
- 验证默认值和类型转换

---

## 🔧 运行测试

### 1. 安装依赖

```bash
cd services/user-service
poetry install
```

### 2. 运行所有测试

```bash
poetry run pytest src/user_service/tests/unit/ -v
```

### 3. 运行特定层级测试

```bash
# 只测试Core层(配置)
poetry run pytest src/user_service/tests/unit/test_core/ -v

# 只测试DAO层
poetry run pytest src/user_service/tests/unit/test_dao/ -v

# 只测试Service层
poetry run pytest src/user_service/tests/unit/test_services/ -v
```

### 4. 运行特定测试文件

```bash
# Core层
poetry run pytest src/user_service/tests/unit/test_core/test_config.py -v

# DAO层
poetry run pytest src/user_service/tests/unit/test_dao/test_customer_profile_dao.py -v
poetry run pytest src/user_service/tests/unit/test_dao/test_provider_profile_dao.py -v

# Service层
poetry run pytest src/user_service/tests/unit/test_services/test_customer_profile_service.py -v
poetry run pytest src/user_service/tests/unit/test_services/test_provider_profile_service.py -v
poetry run pytest src/user_service/tests/unit/test_services/test_admin_user_service.py -v
```

### 5. 生成覆盖率报告

```bash
# 终端输出 + HTML报告
poetry run pytest src/user_service/tests/unit/ \
  --cov=user_service \
  --cov-report=term-missing \
  --cov-report=html

# 查看HTML报告
open htmlcov/index.html
```

### 6. 运行特定测试类

```bash
# Core层配置测试
poetry run pytest src/user_service/tests/unit/test_core/test_config.py::TestSettings -v

# DAO层创建测试
poetry run pytest src/user_service/tests/unit/test_dao/test_customer_profile_dao.py::TestCustomerProfileDAOCreate -v

# Service层创建功能
poetry run pytest src/user_service/tests/unit/test_services/test_customer_profile_service.py::TestCustomerProfileServiceCreate -v
```

### 7. 查看测试执行时间

```bash
poetry run pytest src/user_service/tests/unit/ -v --durations=10
```

---

## 📦 测试依赖

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.4"           # 测试框架
pytest-asyncio = "^0.21.1"  # 异步测试支持
pytest-mock = "^3.15.1"     # Mock对象
pytest-cov = "^4.1.0"       # 覆盖率报告
httpx = "^0.25.2"           # HTTP客户端(跨服务调用)
motor = "^3.3.2"            # MongoDB异步驱动
pydantic-settings = "^2.1.0" # 配置管理
```

---

## 🎓 测试编写最佳实践

### 1. 测试命名规范

```python
# ✅ 好的命名 - 清晰描述测试意图
def test_create_profile_success():
    """成功创建客户档案"""
    
def test_create_profile_already_exists():
    """用户已存在时返回400错误"""
    
def test_update_profile_not_found():
    """更新不存在的档案返回404"""

# ❌ 差的命名 - 不清晰
def test_create():
def test_1():
def test_error():
```

### 2. 测试结构 (AAA模式)

```python
@pytest.mark.asyncio
async def test_create_profile_success(mock_mongo_db, mocker):
    # Arrange - 准备测试数据和Mock
    service = CustomerProfileService(mock_mongo_db)
    mocker.patch.object(service.dao, "get_by_user_id", return_value=None)
    mocker.patch.object(service.dao, "create", return_value=mock_profile)
    
    # Act - 执行被测试方法
    result = await service.create_profile(user_id=1, location="NORTH")
    
    # Assert - 验证结果
    assert result.user_id == 1
    assert result.location == "NORTH"
    service.dao.create.assert_called_once()
```

### 3. Mock对象使用技巧

**DAO层Mock**:
```python
# Mock MongoDB collection
mock_collection = mocker.AsyncMock()
mock_collection.insert_one.return_value.inserted_id = ObjectId()
mock_collection.find_one.return_value = {"user_id": 1, "location": "NORTH"}
```

**Service层Mock**:
```python
# Mock DAO方法
mocker.patch.object(service.dao, "create", return_value=mock_profile)
mocker.patch.object(service.dao, "get_by_id", return_value=None)
```

**事件发布Mock**:
```python
# Mock EventPublisher
mock_publisher = mocker.AsyncMock()
service.event_publisher = mock_publisher

# 验证事件发布
mock_publisher.publish_event.assert_called_once_with(
    "user.customer.created",
    {"user_id": 1}
)
```

### 4. 异常处理测试

```python
@pytest.mark.asyncio
async def test_create_profile_dao_error(service, mocker):
    # Mock抛出异常
    mocker.patch.object(
        service.dao,
        "create",
        side_effect=Exception("Database error")
    )
    
    # 验证异常传播
    with pytest.raises(Exception, match="Database error"):
        await service.create_profile(user_id=1)
```

### 5. 多场景测试 (参数化)

```python
@pytest.mark.asyncio
@pytest.mark.parametrize("hourly_rate_min,hourly_rate_max,expected_count", [
    (0, 100, 5),
    (50, 150, 3),
    (200, 300, 0),
])
async def test_search_by_hourly_rate_range(
    dao, mock_mongo_db, mocker,
    hourly_rate_min, hourly_rate_max, expected_count
):
    # 使用参数化测试多个场景
    mock_cursor = mocker.AsyncMock()
    mock_cursor.limit.return_value.to_list.return_value = [
        {"user_id": i} for i in range(expected_count)
    ]
    
    result = await dao.search(
        hourly_rate_min=hourly_rate_min,
        hourly_rate_max=hourly_rate_max
    )
    
    assert len(result) == expected_count
```

### 6. Fixture使用建议

```python
# conftest.py中定义共享fixture
@pytest.fixture
def sample_customer_profile():
    """返回标准客户档案对象(Model而非dict)"""
    return CustomerProfile(
        user_id=1,
        location="NORTH",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

# 测试中使用fixture
def test_create_with_fixture(sample_customer_profile):
    assert sample_customer_profile.user_id == 1
```

---

## 🚀 下一步计划

### 短期目标

1. ✅ **完成User Service三层测试** (71个测试全部通过)
   - ✅ Core层: 配置管理(10个)
   - ✅ DAO层: CustomerProfile + ProviderProfile(27个)
   - ✅ Service层: 3个服务(34个)

2. ⬜ **补充User Service剩余测试**
   - AdminUserService未覆盖方法 (61%待测试)
   - API路由层集成测试
   - 事件处理器测试

3. ⬜ **应用相同结构到其他服务**
   - Notification Service (最简单,优先)
   - Review Service (MongoDB)
   - Order Service (复杂业务逻辑)
   - Payment Service (外部API集成)

### 长期目标

- 🎯 整体覆盖率达到70%+
- 🎯 所有服务完成Core/DAO/Service三层测试
- 🎯 补充集成测试 (真实数据库)
- 🎯 补充E2E测试 (完整API调用链)

---

## 📚 相关文档

- [Auth Service单元测试](../../auth-service/tests/unit/UNIT_TEST_README.md)
- [快速开始指南](./UNIT_TEST_QUICK_START.md)
- [测试策略文档](../../../../docs/development/testing-guide.md)

---

## 🐛 已知问题

### 1. Pydantic Deprecation警告 (68个)

```
PydanticDeprecatedSince20: Support for class-based `config` is deprecated
```

**影响**: 无,仅为警告,不影响测试功能  
**解决方案**: 将Pydantic模型的`class Config`改为`model_config = ConfigDict(...)`

### 2. datetime.utcnow()警告

```
DeprecationWarning: datetime.datetime.utcnow() is deprecated
```

**影响**: 无,Python 3.13新增警告  
**解决方案**: 使用`datetime.now(datetime.UTC)`替代`datetime.utcnow()`

### 3. AdminUserService覆盖率低 (39%)

**原因**: 部分辅助方法和更新功能未测试  
**计划**: 下一迭代补充测试

---

## 📊 总结

### ✅ 完成情况

- **测试数量**: 71个 (Core 10 + DAO 27 + Service 34)
- **测试通过率**: 100% (0.30s执行时间)
- **覆盖率**: 50% (从29%提升21%)
- **测试结构**: 完整3层架构 ✅

### 🎯 测试质量

- ✅ 所有外部依赖完全Mock (MongoDB/RabbitMQ/HTTP)
- ✅ 异步操作正确处理 (AsyncMock)
- ✅ 边界情况全面覆盖 (异常/空值/不存在)
- ✅ 事件驱动验证 (事件发布测试)

### 📝 经验总结

1. **DAO层测试**: Mock collection方法,注意_id字段处理
2. **Service层测试**: Mock DAO对象,验证事件发布
3. **Core层测试**: patch.dict(os.environ)模拟环境变量
4. **Fixture设计**: 使用Model对象而非dict避免类型错误
5. **MongoDB Mock**: cursor.limit().to_list()模式处理聚合查询

---

**测试版本**: v2.0.0 (Core+DAO+Service完整版)  
**更新时间**: 2025-01-24  
**维护人**: GitHub Copilot  
**测试框架**: pytest 7.4.4 + pytest-asyncio 0.21.1
