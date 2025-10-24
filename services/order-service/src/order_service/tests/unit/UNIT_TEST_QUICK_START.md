# Order Service 单元测试快速入门 / Unit Test Quick Start

## 🚀 快速开始 / Quick Start

### 1. 安装依赖 / Install Dependencies
```bash
cd services/order-service
poetry install
```

### 2. 运行所有测试 / Run All Tests
```bash
poetry run pytest src/order_service/tests/unit/ -v
```

### 3. 查看覆盖率 / Check Coverage
```bash
poetry run pytest src/order_service/tests/unit/ \
  --cov=order_service.services.customer_order_service \
  --cov=order_service.dao \
  --cov=order_service.core.config \
  --cov-report=html
```
覆盖率报告将生成在 `htmlcov/index.html`

## 📊 测试结果 / Test Results

```
====================== 31 passed in 0.21s ======================

Coverage Summary:
- core/config.py:                           100%
- services/customer_order_service.py:       100%
- dao/order_dao.py:                          70%
- Overall:                                   81%
```

## 🎯 常用命令 / Common Commands

### 按类别运行 / Run by Category
```bash
# Core 层测试 (9 tests)
poetry run pytest src/order_service/tests/unit/test_core/ -v

# DAO 层测试 (12 tests)
poetry run pytest src/order_service/tests/unit/test_dao/ -v

# Service 层测试 (10 tests)
poetry run pytest src/order_service/tests/unit/test_services/ -v
```

### 使用标记运行 / Run with Markers
```bash
# 只运行单元测试
poetry run pytest -m unit

# 只运行DAO测试
poetry run pytest -m dao

# 只运行Service测试
poetry run pytest -m service
```

### 调试模式 / Debug Mode
```bash
# 显示print输出
poetry run pytest -s

# 失败时进入调试
poetry run pytest --pdb

# 显示详细错误信息
poetry run pytest -vv
```

## 📁 测试文件结构 / Test File Structure

```
tests/unit/
├── conftest.py                        # 共享fixtures
├── test_core/
│   ├── __init__.py
│   └── test_config.py                 # 配置测试 (9 tests)
├── test_dao/
│   ├── __init__.py
│   └── test_order_dao.py              # DAO测试 (12 tests)
└── test_services/
    ├── __init__.py
    └── test_customer_order_service.py # Service测试 (10 tests)
```

## 🔧 核心测试用例 / Core Test Cases

### Config Tests (100% coverage)
✅ 环境变量加载  
✅ 默认值配置  
✅ URL验证  
✅ 类型检查  

### DAO Tests (70% coverage)
✅ 创建订单 - `create_order()`  
✅ 查询订单 - `get_order_by_id()`, `get_customer_orders()`  
✅ 更新状态 - `update_order_status()`, `accept_order()`  
✅ 更新支付 - `update_payment_status()`  
✅ 删除订单 - `delete_order()`  

### Service Tests (100% coverage)
✅ 发布订单 - `publish_order()`  
✅ 取消订单 - `cancel_order()`  
✅ 查询订单 - `get_my_orders()`, `get_order_detail()`, `get_order_history()`  
✅ HTTP异常 - 404, 403, 400  

## 📝 编写新测试 / Writing New Tests

### 测试模板 / Test Template
```python
import pytest
from unittest.mock import AsyncMock, patch
from order_service.services.customer_order_service import CustomerOrderService
from order_service.dao.order_dao import OrderDAO

class TestNewFeature:
    """Test new feature."""
    
    @pytest.mark.asyncio
    async def test_feature_success(self, mock_db, sample_order):
        """Test successful scenario."""
        # Arrange
        with patch.object(OrderDAO, "some_method", 
                         new_callable=AsyncMock, 
                         return_value=sample_order):
            # Act
            result = await CustomerOrderService.some_method(
                db=mock_db,
                param1="value1"
            )
            
            # Assert
            assert result is not None
            assert result.id == sample_order.id
```

### Fixture 使用 / Using Fixtures
```python
# 使用数据库mock
async def test_with_db(self, mock_db):
    result = await some_dao_method(mock_db)
    mock_db.commit.assert_called_once()

# 使用示例订单
async def test_with_order(self, sample_order):
    assert sample_order.status == OrderStatus.pending_review
    
# 使用事件发布器mock
async def test_with_event(self, mock_event_publisher):
    mock_event_publisher["order_created"].assert_called_once()
```

## 🐛 故障排查 / Troubleshooting

### 常见问题 / Common Issues

#### 1. 异步测试失败
```bash
# 确保使用 @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_method():
    result = await async_function()
```

#### 2. Mock未生效
```bash
# 检查导入路径是否正确
patch.object(OrderDAO, "method_name")  # ✅ 正确
patch("order_dao.method_name")         # ❌ 错误
```

#### 3. SQLAlchemy对象错误
```bash
# 不要使用 __dict__ 解包
Order(**sample_order.__dict__)  # ❌ 错误

# 逐个赋值
Order(
    id=sample_order.id,
    customer_id=sample_order.customer_id,
    ...
)  # ✅ 正确
```

#### 4. 事件发布器KeyError
```bash
# 使用正确的字典键名
mock_event_publisher["order_created"]      # ✅ 正确
mock_event_publisher["publish_order_created"]  # ❌ 错误
```

## 📈 提升覆盖率 / Improving Coverage

### 当前待测试模块 / Untested Modules

1. **ProviderOrderService** (0% coverage)
   - accept_order()
   - start_order()
   - complete_order()
   - get_provider_orders()
   - get_available_orders()

2. **AdminOrderService** (0% coverage)
   - approve_order()
   - reject_order()
   - update_order()
   - delete_order()
   - get_all_orders()

3. **OrderDAO 辅助方法** (未测试)
   - get_provider_orders()
   - get_available_orders()
   - get_all_orders()
   - get_orders_by_status()

## 🎓 最佳实践 / Best Practices

### 1. 测试命名
```python
# ✅ 好的命名
test_publish_order_success
test_cancel_order_not_found
test_get_order_detail_permission_denied

# ❌ 差的命名
test_1
test_order
test_function
```

### 2. AAA 模式
```python
async def test_example():
    # Arrange - 准备测试数据
    order = create_sample_order()
    
    # Act - 执行被测试的操作
    result = await service.process(order)
    
    # Assert - 验证结果
    assert result.status == "success"
```

### 3. Mock 策略
```python
# 只Mock外部依赖
with patch.object(OrderDAO, "get_order_by_id"):  # ✅ Mock DAO
    result = await service.get_order()

# 不要Mock被测试的类本身
with patch.object(CustomerOrderService, "get_order"):  # ❌ 错误
```

### 4. 异常测试
```python
# 使用 pytest.raises
with pytest.raises(HTTPException) as exc_info:
    await service.cancel_order(order_id=999)
    
assert exc_info.value.status_code == 404
assert "not found" in exc_info.value.detail.lower()
```

## 📚 更多资源 / More Resources

- **详细文档**: `TEST_SUMMARY.md` - 完整测试报告
- **实现文档**: `UNIT_TEST_README.md` - 测试实现指南
- **示例代码**: `test_services/test_customer_order_service.py` - 参考示例

---

**快速链接 / Quick Links**:
- [pytest 文档](https://docs.pytest.org/)
- [pytest-asyncio 文档](https://pytest-asyncio.readthedocs.io/)
- [Order Service API 文档](../../docs/api/order-service.md)

**需要帮助？/ Need Help?**  
查看 `TEST_SUMMARY.md` 了解更多详情
