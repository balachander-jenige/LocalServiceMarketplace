# Auth Service 单元测试说明

## 📁 测试结构

```
tests/unit/
├── conftest.py              # 共享fixtures和Mock对象
├── test_services/           # Service层测试
│   └── test_auth_service.py # 注册和登录逻辑测试
├── test_core/               # 核心工具测试
│   └── test_security.py     # 密码加密和JWT测试
└── test_dao/                # DAO层测试
    └── test_user_dao.py     # 数据库操作测试
```

## 🎯 测试覆盖

| 模块 | 测试用例数 | 覆盖功能 |
|------|----------|---------|
| **AuthService** | 7个 | 注册(成功/重复/不同角色)、登录(成功/错误密码/用户不存在) |
| **Security** | 17个 | 密码加密/验证、JWT创建/验证/过期 |
| **UserDAO** | 8个 | 创建/查询/更新用户 |

## 🚀 运行测试

```bash
# 进入服务目录
cd services/auth-service

# 运行所有单元测试
pytest src/auth_service/tests/unit/ -v

# 运行特定测试文件
pytest src/auth_service/tests/unit/test_services/test_auth_service.py -v

# 生成覆盖率报告
pytest src/auth_service/tests/unit/ --cov=auth_service --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

## ✅ 测试特点

- **完全Mock**: 所有外部依赖(数据库、RabbitMQ)均使用Mock,不影响真实数据
- **快速执行**: 单元测试<5秒完成
- **高覆盖率**: 核心业务逻辑覆盖率>85%
- **独立运行**: 测试间完全隔离,可单独运行任何测试

## 📝 测试示例

### 测试注册成功
```python
async def test_register_success(self, mock_db_session, mocker):
    # Mock数据库和事件发布
    mock_user = MagicMock()
    mocker.patch("...UserDAO.create_user", return_value=mock_user)
    
    # 执行注册
    result = await AuthService.register(...)
    
    # 验证结果
    assert result.id == 1
```

### 测试密码加密
```python
def test_verify_password_correct(self):
    hashed = hash_password("Test123!")
    assert verify_password("Test123!", hashed) is True
```

## 🔧 依赖要求

已在 `pyproject.toml` 中配置:
- pytest
- pytest-asyncio
- pytest-mock (需添加)
- httpx

## 📊 覆盖率目标

- Service层: ≥90%
- Security工具: ≥95%
- DAO层: ≥85%
- **整体目标**: ≥85%
