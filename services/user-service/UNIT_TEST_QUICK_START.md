# User Service 单元测试快速开始

## 🚀 5分钟快速上手

### 1. 安装依赖 (30秒)

```bash
cd services/user-service
poetry install
```

### 2. 运行测试 (10秒)

```bash
poetry run pytest src/user_service/tests/unit/ -v
```

**预期输出**:
```
========== 34 passed, 32 warnings in 0.61s ==========
```

### 3. 查看覆盖率 (20秒)

```bash
poetry run pytest src/user_service/tests/unit/ \
  --cov=user_service \
  --cov-report=html

open htmlcov/index.html  # macOS
```

## 📋 常用命令

### 测试命令

```bash
# 运行所有单元测试
poetry run pytest src/user_service/tests/unit/ -v

# 只运行Customer服务测试
poetry run pytest src/user_service/tests/unit/test_services/test_customer_profile_service.py -v

# 只运行Provider服务测试
poetry run pytest src/user_service/tests/unit/test_services/test_provider_profile_service.py -v

# 只运行Admin服务测试
poetry run pytest src/user_service/tests/unit/test_services/test_admin_user_service.py -v

# 运行特定测试
poetry run pytest src/user_service/tests/unit/test_services/test_customer_profile_service.py::TestCustomerProfileServiceCreate::test_create_profile_success -v

# 显示详细错误信息
poetry run pytest src/user_service/tests/unit/ -v --tb=short
```

### 覆盖率命令

```bash
# 终端显示 + HTML报告
poetry run pytest src/user_service/tests/unit/ --cov=user_service --cov-report=term --cov-report=html

# 只生成终端报告
poetry run pytest src/user_service/tests/unit/ --cov=user_service --cov-report=term

# 只生成HTML报告
poetry run pytest src/user_service/tests/unit/ --cov=user_service --cov-report=html
```

## 📊 测试概览

| 测试文件 | 测试数量 | 覆盖模块 | 状态 |
|---------|---------|---------|------|
| test_customer_profile_service.py | 11 | CustomerProfileService | ✅ |
| test_provider_profile_service.py | 18 | ProviderProfileService | ✅ |
| test_admin_user_service.py | 8 | AdminUserService | ✅ |

**总计**: 34个测试,全部通过 ✅

## 🎯 测试结构

```
src/user_service/tests/unit/
├── conftest.py                         # 共享Fixtures
└── test_services/
    ├── test_customer_profile_service.py
    │   ├── TestCustomerProfileServiceCreate (4个)
    │   ├── TestCustomerProfileServiceGet (2个)
    │   └── TestCustomerProfileServiceUpdate (5个)
    ├── test_provider_profile_service.py
    │   ├── TestProviderProfileServiceCreate (4个)
    │   ├── TestProviderProfileServiceGet (2个)
    │   ├── TestProviderProfileServiceUpdate (5个)
    │   └── TestProviderProfileServiceSearch (5个)
    └── test_admin_user_service.py
        ├── TestAdminUserServiceGetAllUsers (3个)
        └── TestAdminUserServiceGetUserDetail (5个)
```

## 🔧 快速调试

### 运行失败的测试

```bash
# 只运行上次失败的测试
poetry run pytest --lf

# 运行失败的测试并停止在第一个失败
poetry run pytest --lf --exitfirst
```

### 查看详细输出

```bash
# 显示print输出
poetry run pytest src/user_service/tests/unit/ -v -s

# 显示局部变量
poetry run pytest src/user_service/tests/unit/ -v --tb=long --showlocals
```

### 性能分析

```bash
# 显示最慢的10个测试
poetry run pytest src/user_service/tests/unit/ --durations=10
```

## ✅ 健康检查

运行以下命令确保测试环境正常:

```bash
# 1. 检查依赖
poetry show pytest pytest-asyncio pytest-mock pytest-cov

# 2. 验证配置
cat pytest.ini

# 3. 运行测试
poetry run pytest src/user_service/tests/unit/ -v

# 4. 检查覆盖率
poetry run pytest src/user_service/tests/unit/ --cov=user_service --cov-report=term | tail -20
```

**预期结果**:
- ✅ 所有依赖已安装
- ✅ pytest.ini配置正确
- ✅ 34个测试全部通过
- ✅ 核心服务模块覆盖率100%

## 🐛 常见问题

### Q1: ImportError: No module named 'user_service'

**解决**:
```bash
poetry install
```

### Q2: 测试运行很慢

**检查**:
```bash
# 确保使用asyncio_mode = auto
cat pytest.ini | grep asyncio_mode
```

### Q3: Mock对象报错 "coroutine object is not subscriptable"

**原因**: HTTP response Mock应该用`MagicMock`而不是`AsyncMock`

**正确写法**:
```python
mock_response = MagicMock()  # 不是AsyncMock()
mock_response.status_code = 200
mock_response.json.return_value = {"data": "test"}
```

### Q4: 看到很多Pydantic警告

**说明**: 这是Pydantic V2的deprecation警告,不影响测试功能

**忽略方法**:
```bash
poetry run pytest src/user_service/tests/unit/ -v --disable-warnings
```

## 📚 下一步

1. ✅ 熟悉测试结构和运行方式
2. ⬜ 阅读[完整文档](./UNIT_TEST_README.md)了解Mock策略
3. ⬜ 学习如何编写新的测试用例
4. ⬜ 查看[测试策略文档](../../docs/development/testing-guide.md)

## 🔗 相关链接

- [完整测试文档](./UNIT_TEST_README.md)
- [Auth Service测试](../auth-service/UNIT_TEST_README.md)
- [项目贡献指南](../../CONTRIBUTING.md)

---

**快速帮助**: 如有问题,请查看[完整文档](./UNIT_TEST_README.md)或联系团队
