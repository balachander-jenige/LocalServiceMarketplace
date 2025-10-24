# Order Service 单元测试实现文档 / Unit Test Implementation Guide

## 📖 概述 / Overview

本文档详细说明了 Order Service 的单元测试实现细节，包括架构设计、Mock策略、测试用例设计和最佳实践。

This document provides detailed information about Order Service unit test implementation, including architecture design, mocking strategies, test case design, and best practices.

## 🏗️ 架构设计 / Architecture Design

### 分层测试策略 / Layered Testing Strategy

```
┌─────────────────────────────────────────┐
│         API Layer (未测试)               │  ← 集成测试覆盖
│            (FastAPI)                     │     Integration tests
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│      Service Layer (100%)                │  ← 业务逻辑测试
│  - CustomerOrderService                  │     Business logic tests
│  - ProviderOrderService (待实现)         │
│  - AdminOrderService (待实现)            │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        DAO Layer (70%)                   │  ← 数据访问测试
│        - OrderDAO                        │     Data access tests
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│       Model Layer (隐式测试)             │  ← 通过上层测试覆盖
│        - Order Model                     │     Covered by upper layers
│        - Enums                           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      Core Layer (100%)                   │  ← 配置管理测试
│        - Settings                        │     Configuration tests
└─────────────────────────────────────────┘
```

### 测试依赖图 / Test Dependency Graph

```
conftest.py
    ├── mock_db (AsyncSession Mock)
    │   └── 所有DAO和Service测试
    │
    ├── sample_order (pending_review)
    │   ├── test_cancel_order_*
    │   └── test_get_order_detail_*
    │
    ├── sample_pending_order
    │   └── test_accept_order_*
    │
    ├── sample_accepted_order
    │   └── test_start_order_* (待实现)
    │
    └── mock_event_publisher
        ├── order_created
        ├── order_cancelled
        ├── order_accepted
        ├── order_status_changed
        ├── order_approved
        └── order_rejected
```

## 🔧 技术实现 / Technical Implementation

### 1. pytest 配置 / pytest Configuration

**文件**: `pytest.ini`

```ini
[pytest]
# 异步测试模式: auto - 自动检测async函数
asyncio_mode = auto

# 测试标记定义
markers =
    unit: Unit tests for individual components
    dao: DAO layer tests
    service: Service layer tests
    core: Core configuration tests

# Python 路径配置
pythonpath = src

# 测试发现模式
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**关键配置说明**:
- `asyncio_mode = auto`: 自动识别并运行异步测试
- `pythonpath = src`: 设置模块搜索路径
- 标记系统: 支持按功能模块筛选测试

### 2. 依赖管理 / Dependency Management

**文件**: `pyproject.toml`

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.4"           # 核心测试框架
pytest-asyncio = "^0.21.2"  # 异步测试支持
pytest-cov = "^4.1.0"       # 覆盖率报告
pytest-mock = "^3.12.0"     # Mock增强工具
```

**依赖选择理由**:
- **pytest**: 业界标准，功能强大的测试框架
- **pytest-asyncio**: Order Service大量使用async/await
- **pytest-cov**: 精确的代码覆盖率分析
- **pytest-mock**: 简化Mock对象创建

### 3. Fixture 设计 / Fixture Design

**文件**: `conftest.py`

#### 3.1 数据库 Mock (`mock_db`)

```python
@pytest.fixture
def mock_db():
    """Mock AsyncSession for database operations."""
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.get = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.delete = AsyncMock()
    return mock_session
```

**设计考虑**:
- **spec=AsyncSession**: 确保类型安全
- **AsyncMock**: 支持 `await` 调用
- **MagicMock**: 用于同步方法（add）

**使用示例**:
```python
async def test_create_order(mock_db):
    order = await OrderDAO.create_order(mock_db, title="Test")
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
```

#### 3.2 测试数据 Fixtures

##### sample_order (pending_review 状态)
```python
@pytest.fixture
def sample_order():
    """Sample order in pending_review status."""
    return Order(
        id=1,
        customer_id=10,
        title="Test Order",
        description="Test description",
        service_type=ServiceType.CLEANING_REPAIR,
        status=OrderStatus.pending_review,
        price=100.00,
        location=LocationEnum.NORTH,
        address="123 Main St",
        payment_status=PaymentStatus.unpaid,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
```

**用途**: 
- 测试订单取消（pending_review可取消）
- 测试订单查询权限验证
- 测试管理员审批流程

##### sample_pending_order
```python
@pytest.fixture
def sample_pending_order():
    """Sample order in pending status (approved by admin)."""
    return Order(
        id=2,
        customer_id=10,
        provider_id=None,
        title="Test Pending Order",
        status=OrderStatus.pending,  # 已审批，等待接单
        ...
    )
```

**用途**:
- 测试服务商接单
- 测试可用订单列表

##### sample_accepted_order
```python
@pytest.fixture
def sample_accepted_order():
    """Sample order in accepted status (taken by provider)."""
    return Order(
        id=3,
        provider_id=20,
        status=OrderStatus.accepted,  # 已接单
        ...
    )
```

**用途**:
- 测试服务商开始服务
- 测试订单进度更新

#### 3.3 事件发布器 Mock

```python
@pytest.fixture
def mock_event_publisher(mocker):
    """Mock EventPublisher for testing event publishing."""
    mock_order_created = mocker.patch(
        "order_service.services.customer_order_service.EventPublisher.publish_order_created",
        new_callable=AsyncMock
    )
    # ... 其他5个事件mock
    
    return {
        "order_created": mock_order_created,
        "order_cancelled": mock_order_cancelled,
        "order_accepted": mock_order_accepted,
        "order_status_changed": mock_order_status_changed,
        "order_approved": mock_order_approved,
        "order_rejected": mock_order_rejected,
    }
```

**设计亮点**:
1. **字典返回**: 方便访问特定事件mock
2. **完整路径**: 精确patch到使用位置
3. **AsyncMock**: 支持异步事件发布

**使用示例**:
```python
async def test_publish_order(mock_event_publisher):
    await CustomerOrderService.publish_order(...)
    mock_event_publisher["order_created"].assert_called_once()
```

#### 3.4 Service Fixtures

```python
@pytest.fixture
def customer_order_service(mock_db, mock_event_publisher):
    """CustomerOrderService instance with mocked dependencies."""
    return CustomerOrderService(db=mock_db)

@pytest.fixture
def provider_order_service(mock_db, mock_event_publisher):
    """ProviderOrderService instance with mocked dependencies."""
    return ProviderOrderService(db=mock_db)

@pytest.fixture
def admin_order_service(mock_db, mock_event_publisher):
    """AdminOrderService instance with mocked dependencies."""
    return AdminOrderService(db=mock_db)
```

**用途**: 
- 简化Service层测试代码
- 自动注入所需依赖
- 支持未来扩展

## 🧪 测试用例设计 / Test Case Design

### 1. Core Layer Tests

#### 文件结构
```
test_core/
├── __init__.py
└── test_config.py (9 tests)
```

#### 测试类组织
```python
class TestSettings:
    """Test Settings configuration."""
    
    # 基础测试
    def test_settings_with_env_vars(self, monkeypatch): ...
    def test_settings_default_values(self): ...
    def test_settings_required_fields(self, monkeypatch): ...
    
    # 验证测试
    def test_settings_database_url_validation(self, monkeypatch): ...
    def test_settings_rabbitmq_url_validation(self, monkeypatch): ...
    def test_settings_service_port_type(self, monkeypatch): ...
    
    # 覆盖测试
    def test_settings_service_urls_override(self, monkeypatch): ...
    def test_settings_log_level_values(self, monkeypatch): ...
    def test_settings_service_name_custom(self, monkeypatch): ...
```

#### 测试策略
| 测试类型 | 数量 | 目标 |
|---------|------|------|
| 环境变量加载 | 1 | 验证env vars正确读取 |
| 默认值 | 1 | 验证默认配置正确 |
| 必填字段 | 1 | 验证必填项存在 |
| 数据验证 | 3 | URL格式、端口类型验证 |
| 覆盖机制 | 3 | 验证配置可覆盖 |

**关键技术**:
```python
# 使用 monkeypatch 修改环境变量
monkeypatch.setenv("DATABASE_URL", "mysql://test")
monkeypatch.delenv("SERVICE_NAME", raising=False)

# 验证 Pydantic 配置
settings = Settings()
assert settings.DATABASE_URL == "mysql://test"
```

### 2. DAO Layer Tests

#### 文件结构
```
test_dao/
├── __init__.py
└── test_order_dao.py (12 tests)
```

#### 测试类组织
```python
# Create操作 (1 test)
class TestOrderDAOCreate:
    async def test_create_order_success(self, mock_db): ...

# Read操作 (4 tests)
class TestOrderDAOGet:
    async def test_get_order_by_id_success(self, mock_db): ...
    async def test_get_order_by_id_not_found(self, mock_db): ...
    async def test_get_customer_orders_success(self, mock_db): ...
    async def test_get_customer_orders_with_status_filter(self, mock_db): ...

# Update操作 (4 tests)
class TestOrderDAOUpdate:
    async def test_update_order_status_success(self, mock_db, sample_order): ...
    async def test_update_order_status_not_found(self, mock_db): ...
    async def test_accept_order_success(self, mock_db, sample_pending_order): ...
    async def test_update_payment_status_success(self, mock_db, sample_order): ...

# Delete操作 (2 tests)
class TestOrderDAODelete:
    async def test_delete_order_success(self, mock_db, sample_order): ...
    async def test_delete_order_not_found(self, mock_db): ...
```

#### Mock 策略

##### 方式1: patch.object (推荐)
```python
from unittest.mock import patch, AsyncMock

async def test_example(mock_db):
    with patch.object(OrderDAO, "get_order_by_id", 
                     new_callable=AsyncMock, 
                     return_value=sample_order):
        result = await OrderDAO.get_order_by_id(mock_db, order_id=1)
        assert result.id == 1
```

**优点**:
- ✅ 精确控制返回值
- ✅ 支持复杂场景模拟
- ✅ 易于验证调用

##### 方式2: Mock execute结果
```python
async def test_example(mock_db):
    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=[order1, order2])))
    mock_db.execute.return_value = mock_result
    
    result = await OrderDAO.get_customer_orders(mock_db, customer_id=10)
    assert len(result) == 2
```

**优点**:
- ✅ 更接近真实SQL执行流程
- ✅ 测试SQLAlchemy查询构建

#### 测试覆盖矩阵

| DAO Method | Success | Not Found | Error | 状态 |
|-----------|---------|-----------|-------|------|
| create_order | ✅ | - | - | 已测试 |
| get_order_by_id | ✅ | ✅ | - | 已测试 |
| get_customer_orders | ✅ | - | - | 已测试 |
| get_customer_orders (filter) | ✅ | - | - | 已测试 |
| update_order_status | ✅ | ✅ | - | 已测试 |
| accept_order | ✅ | - | - | 已测试 |
| update_payment_status | ✅ | - | - | 已测试 |
| delete_order | ✅ | ✅ | - | 已测试 |
| get_provider_orders | - | - | - | 未测试 |
| get_available_orders | - | - | - | 未测试 |
| get_all_orders | - | - | - | 未测试 |
| get_orders_by_status | - | - | - | 未测试 |

### 3. Service Layer Tests

#### 文件结构
```
test_services/
├── __init__.py
├── test_customer_order_service.py (10 tests)
├── test_provider_order_service.py (未实现)
└── test_admin_order_service.py (未实现)
```

#### CustomerOrderService 测试矩阵

| 方法 | 成功 | 404 | 403 | 400 | 状态 |
|-----|------|-----|-----|-----|------|
| publish_order | ✅✅ | - | - | - | 完成 |
| cancel_order | ✅ | ✅ | ✅ | ✅ | 完成 |
| get_my_orders | ✅ | - | - | - | 完成 |
| get_order_detail | ✅ | ✅ | ✅ | - | 完成 |
| get_order_history | ✅ | - | - | - | 完成 |

**测试细节**:

##### publish_order (2 tests)
```python
class TestCustomerOrderServicePublishOrder:
    async def test_publish_order_success(self, mock_db, mock_event_publisher):
        """测试基本发布流程."""
        with patch.object(OrderDAO, "create_order", new_callable=AsyncMock, return_value=created_order):
            order = await CustomerOrderService.publish_order(...)
            
            # 验证订单状态
            assert order.status == OrderStatus.pending_review
            # 验证事件发布
            mock_event_publisher["order_created"].assert_called_once()
    
    async def test_publish_order_with_service_time(self, mock_db):
        """测试带服务时间的订单."""
        order = await CustomerOrderService.publish_order(
            service_start_time=datetime.now() + timedelta(days=1),
            service_end_time=datetime.now() + timedelta(days=2)
        )
        assert order.service_start_time is not None
```

##### cancel_order (4 tests)
```python
class TestCustomerOrderServiceCancelOrder:
    async def test_cancel_order_success(self, mock_db, sample_order, mock_event_publisher):
        """成功取消订单."""
        cancelled_order = Order(...)  # 创建cancelled状态的订单
        with patch.object(OrderDAO, "get_order_by_id", return_value=sample_order):
            with patch.object(OrderDAO, "update_order_status", return_value=cancelled_order):
                order = await CustomerOrderService.cancel_order(...)
                assert order.status == OrderStatus.cancelled
                mock_event_publisher["order_cancelled"].assert_called_once()
    
    async def test_cancel_order_not_found(self, mock_db):
        """订单不存在 - 404."""
        with patch.object(OrderDAO, "get_order_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                await CustomerOrderService.cancel_order(...)
            assert exc_info.value.status_code == 404
    
    async def test_cancel_order_permission_denied(self, mock_db, sample_order):
        """权限拒绝 - 403."""
        with patch.object(OrderDAO, "get_order_by_id", return_value=sample_order):
            with pytest.raises(HTTPException) as exc_info:
                await CustomerOrderService.cancel_order(
                    customer_id=99999  # 不同的customer_id
                )
            assert exc_info.value.status_code == 403
    
    async def test_cancel_order_invalid_status(self, mock_db):
        """无效状态 - 400."""
        completed_order = Order(..., status=OrderStatus.completed)
        with patch.object(OrderDAO, "get_order_by_id", return_value=completed_order):
            with pytest.raises(HTTPException) as exc_info:
                await CustomerOrderService.cancel_order(...)
            assert exc_info.value.status_code == 400
```

**HTTP异常测试模式**:
```python
# 标准异常测试结构
with pytest.raises(HTTPException) as exc_info:
    await service_method(...)

# 验证状态码
assert exc_info.value.status_code == 404

# 验证错误消息
assert "not found" in exc_info.value.detail.lower()
```

## 📊 覆盖率分析 / Coverage Analysis

### 覆盖率报告解读

```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
core/config.py                             13      0   100%
dao/__init__.py                             2      0   100%
dao/order_dao.py                          101     30    70%   71-74, 86-102, ...
services/customer_order_service.py         43      0   100%
---------------------------------------------------------------------
TOTAL                                     159     30    81%
```

#### 未覆盖代码分析

##### dao/order_dao.py (71-74行)
```python
# Lines 71-74: get_provider_orders - 辅助查询方法
async def get_provider_orders(cls, db: AsyncSession, provider_id: int, status: OrderStatus = None):
    """Get orders for a specific provider."""
    # 未测试: 需要ProviderOrderService测试
```

##### dao/order_dao.py (86-102行)
```python
# Lines 86-102: get_available_orders - 公开订单列表
async def get_available_orders(cls, db: AsyncSession, location: LocationEnum = None):
    """Get available orders (pending status, no provider assigned)."""
    # 未测试: 需要ProviderOrderService测试
```

**改进计划**:
1. 添加 ProviderOrderService 测试 → 提升DAO覆盖至 85%
2. 添加 AdminOrderService 测试 → 提升DAO覆盖至 95%+

### 测试质量指标

| 指标 | 当前值 | 目标值 | 状态 |
|-----|--------|-------|------|
| 总测试数 | 31 | 45+ | 🔄 进行中 |
| 通过率 | 100% | 100% | ✅ 达标 |
| 覆盖率 | 81% | 95%+ | 🔄 提升中 |
| 执行时间 | 0.21s | <0.5s | ✅ 优秀 |
| 异常测试 | 6 | 10+ | 🔄 增加中 |

## 🎯 最佳实践 / Best Practices

### 1. 测试命名规范

#### ✅ 好的命名
```python
# 模式: test_<method>_<scenario>
test_create_order_success
test_cancel_order_not_found
test_get_order_detail_permission_denied
test_update_order_status_invalid_status
```

#### ❌ 差的命名
```python
test_1
test_order
test_function
test_it_works
```

### 2. AAA 模式应用

```python
@pytest.mark.asyncio
async def test_example(mock_db, sample_order):
    # === Arrange ===
    # 准备测试数据和Mock
    with patch.object(OrderDAO, "get_order_by_id", 
                     return_value=sample_order):
        
        # === Act ===
        # 执行被测试的操作
        result = await CustomerOrderService.get_order_detail(
            db=mock_db,
            order_id=1,
            customer_id=10
        )
        
        # === Assert ===
        # 验证结果
        assert result.id == 1
        assert result.customer_id == 10
```

### 3. SQLAlchemy 对象处理

#### ❌ 错误方式
```python
# 不要使用 __dict__ 解包
new_order = Order(**sample_order.__dict__)
# TypeError: '_sa_instance_state' is an invalid keyword argument
```

#### ✅ 正确方式
```python
# 方式1: 逐个赋值
new_order = Order(
    id=sample_order.id,
    customer_id=sample_order.customer_id,
    title=sample_order.title,
    ...
)

# 方式2: 使用from_orm (Pydantic模型)
order_data = OrderDTO.from_orm(sample_order)
```

### 4. 异步测试最佳实践

```python
# 1. 总是使用 @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_method():
    result = await some_async_function()

# 2. Mock 异步方法使用 AsyncMock
mock_method = AsyncMock(return_value="result")

# 3. 验证异步调用
await mock_method("arg")
mock_method.assert_called_once_with("arg")

# 4. 嵌套 patch.object 支持多个Mock
with patch.object(OrderDAO, "method1", new_callable=AsyncMock):
    with patch.object(OrderDAO, "method2", new_callable=AsyncMock):
        result = await service_method()
```

### 5. 事件发布测试

```python
@pytest.mark.asyncio
async def test_event_publishing(mock_event_publisher):
    # Act
    await CustomerOrderService.publish_order(...)
    
    # Assert - 验证事件被调用
    mock_event_publisher["order_created"].assert_called_once()
    
    # 验证事件参数
    call_args = mock_event_publisher["order_created"].call_args
    event = call_args[0][0]  # 第一个位置参数
    assert event.order_id == 1
    assert event.customer_id == 10
```

### 6. HTTPException 测试模式

```python
# 标准模式
with pytest.raises(HTTPException) as exc_info:
    await service_method(...)

# 验证状态码
assert exc_info.value.status_code == 404

# 验证错误消息
assert "order not found" in exc_info.value.detail.lower()

# 验证headers (如果有)
assert "X-Error-Code" in exc_info.value.headers
```

## 🔍 调试技巧 / Debugging Tips

### 1. 显示详细输出
```bash
# 显示print输出
poetry run pytest -s

# 显示详细日志
poetry run pytest -v -v

# 显示所有局部变量
poetry run pytest -l
```

### 2. 失败时进入调试器
```bash
poetry run pytest --pdb

# 或在代码中设置断点
import pdb; pdb.set_trace()
```

### 3. 只运行失败的测试
```bash
poetry run pytest --lf  # last-failed

poetry run pytest --ff  # failed-first
```

### 4. 查看覆盖率详情
```bash
# HTML报告
poetry run pytest --cov-report=html
open htmlcov/index.html

# 终端详细报告
poetry run pytest --cov-report=term-missing
```

### 5. Mock验证失败调试
```python
# 查看所有调用
print(mock_method.call_args_list)

# 查看调用次数
print(mock_method.call_count)

# 重置Mock
mock_method.reset_mock()
```

## 📈 持续改进 / Continuous Improvement

### 短期目标 (1-2周)
- [ ] 完成 ProviderOrderService 测试 (10个测试)
- [ ] 完成 AdminOrderService 测试 (8个测试)
- [ ] 提升DAO覆盖率到 90%+
- [ ] 总覆盖率达到 90%+

### 中期目标 (1个月)
- [ ] 添加集成测试
- [ ] 添加性能测试
- [ ] 添加并发测试
- [ ] CI/CD集成

### 长期目标 (3个月)
- [ ] E2E测试覆盖
- [ ] 压力测试
- [ ] 安全测试
- [ ] 测试文档自动生成

## 📚 参考资源 / References

### 官方文档
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### 内部文档
- `TEST_SUMMARY.md` - 测试总结报告
- `UNIT_TEST_QUICK_START.md` - 快速入门指南
- Review Service 测试实现 - 参考示例

### 推荐阅读
- "Test Driven Development" - Kent Beck
- "Growing Object-Oriented Software, Guided by Tests" - Steve Freeman
- "The Art of Unit Testing" - Roy Osherove

---

**版本 / Version**: 1.0.0  
**最后更新 / Last Updated**: 2025-01-24  
**维护者 / Maintainer**: Development Team
