# CI 单元测试工作流说明

**创建日期**: 2025-10-24  
**状态**: ✅ 已添加

---

## 📋 概述

已为项目添加单元测试 CI 工作流，在每次推送到 `reid` 分支时自动运行所有微服务的单元测试。

---

## 🎯 触发条件

### 自动触发
- **Push 到 reid 分支**，且修改了以下文件：
  - `services/**/*.py`
  - `gateway-service/**/*.py`
  - `shared/**/*.py`
  - `.github/workflows/backend-unit-tests.yml`

- **Pull Request 到 reid 分支**，且修改了相同文件

### 手动触发
- 支持通过 GitHub Actions 界面手动触发（`workflow_dispatch`）

---

## 🏗️ 工作流结构

### Job 1: unit-tests

**并行执行策略**（Matrix Strategy）:
- 同时运行 6 个微服务的单元测试
- 失败不中断其他服务测试（`fail-fast: false`）

**测试的服务**:
1. auth-service
2. user-service
3. order-service
4. payment-service
5. review-service
6. notification-service

**执行步骤**:

1. **Checkout 代码**
   ```yaml
   uses: actions/checkout@v4
   ```

2. **设置 Python 3.11 环境**
   ```yaml
   uses: actions/setup-python@v5
   ```

3. **安装 Poetry**
   - 使用官方安装脚本
   - 添加到 PATH

4. **配置 Poetry**
   ```bash
   poetry config virtualenvs.create true
   poetry config virtualenvs.in-project true
   ```

5. **缓存依赖**
   - 缓存每个服务的 `.venv` 目录
   - 基于 `pyproject.toml` 哈希值

6. **安装依赖**
   ```bash
   poetry install --no-interaction
   ```
   注意：不使用 `--no-root`，确保服务本身被安装为可导入的包

7. **设置测试环境变量**
   ```bash
   # Database URLs
   DATABASE_URL: "mysql+aiomysql://test:test@localhost:3306/test_db"
   MONGODB_URL: "mongodb://test:test@localhost:27017/test_db"
   
   # Message Queue & Cache
   RABBITMQ_URL: "amqp://guest:guest@localhost:5672/"
   REDIS_URL: "redis://localhost:6379/0"
   
   # Auth Service specific
   JWT_SECRET_KEY: "test-secret-key-for-ci"
   LOCAL_RABBITMQ_URL: "amqp://guest:guest@localhost:5672/"
   DOCKER_RABBITMQ_URL: "amqp://guest:guest@localhost:5672/"
   
   # Service URLs (for inter-service communication)
   AUTH_SERVICE_URL: "http://localhost:8000"
   USER_SERVICE_URL: "http://localhost:8002"
   ORDER_SERVICE_URL: "http://localhost:8003"
   PAYMENT_SERVICE_URL: "http://localhost:8004"
   REVIEW_SERVICE_URL: "http://localhost:8005"
   ```
   注意：这些是测试专用的环境变量，单元测试使用 mock，不会真正连接数据库或其他服务

8. **运行单元测试**
   - 自动根据服务选择正确的覆盖率配置
   - 生成终端报告和 XML 报告
   - **覆盖率要求: ≥ 90%**

9. **上传覆盖率报告**
   - 保存为 Artifacts
   - 保留 30 天

### Job 2: test-summary

**依赖**: 等待所有单元测试完成

**执行内容**:
- 显示测试执行摘要
- 验证所有测试是否通过
- 如有失败则返回错误码

---

## 📊 各服务覆盖率配置

### Auth Service
```bash
--cov=auth_service.core.security \
--cov=auth_service.dao \
--cov=auth_service.services
```

### User Service
```bash
--cov=user_service.core.config \
--cov=user_service.dao \
--cov=user_service.services
```

### Order Service
```bash
--cov=order_service.core.config \
--cov=order_service.services
```

### Payment Service
```bash
--cov=payment_service.core.config \
--cov=payment_service.dao.payment_dao \
--cov=payment_service.services
```

### Review Service
```bash
--cov=review_service.core.config \
--cov=review_service.dao \
--cov=review_service.services
```

### Notification Service
```bash
--cov=notification_service.core.config \
--cov=notification_service.dao \
--cov=notification_service.services
```

---

## ✅ 覆盖率标准

| 指标 | 要求 |
|------|------|
| **核心模块覆盖率** | ≥ 90% |
| **测试通过率** | 100% |
| **报告格式** | Terminal + XML |

---

## 🚀 本地测试验证

在推送前可以本地验证：

```bash
# 测试所有服务
./scripts/regenerate-coverage.sh

# 测试单个服务
cd services/auth-service
poetry run pytest src/auth_service/tests/unit/ -v \
  --cov=auth_service.core.security \
  --cov=auth_service.dao \
  --cov=auth_service.services \
  --cov-fail-under=90
```

---

## 📁 CI 工作流文件

**文件位置**: `.github/workflows/backend-unit-tests.yml`

**相关工作流**:
- `backend-lint.yml` - 代码格式和风格检查
- `backend-sast.yml` - 安全扫描
- `backend-unit-tests.yml` - 单元测试（新增）
- `dev-deploy.yaml` - 部署到 EKS

---

## 🔍 查看测试结果

### 在 GitHub Actions 界面

1. 进入仓库的 **Actions** 标签
2. 选择 **Backend Unit Tests** 工作流
3. 查看最新的运行记录
4. 展开各个服务的测试结果

### 下载覆盖率报告

1. 在工作流运行详情页
2. 滚动到底部的 **Artifacts** 区域
3. 下载对应服务的覆盖率报告：
   - `coverage-auth-service`
   - `coverage-user-service`
   - `coverage-order-service`
   - `coverage-payment-service`
   - `coverage-review-service`
   - `coverage-notification-service`

---

## ⚡ 性能优化

### 依赖缓存
- 使用 GitHub Actions Cache
- 基于 `pyproject.toml` 哈希
- 显著减少依赖安装时间

### 并行执行
- 6 个服务同时运行
- 总执行时间约为最慢服务的时间
- 预计总耗时: **2-3 分钟**

### 缓存策略
```yaml
key: poetry-${{ matrix.service }}-${{ runner.os }}-${{ hashFiles(...) }}
restore-keys: |
  poetry-${{ matrix.service }}-${{ runner.os }}-
```

---

## 🎯 质量保证

### 自动化检查
- ✅ 代码格式检查（Black, isort）
- ✅ 代码风格检查（Flake8）
- ✅ 安全扫描（Bandit）
- ✅ **单元测试（Pytest）**（新增）

### 覆盖率要求
- **核心模块**: ≥ 90%
- **当前状态**: 99.3% 平均
- **测试数量**: 330 个

---

## 📝 注意事项

1. **覆盖率失败会阻塞工作流**
   - 如果核心覆盖率低于 90%，测试会失败
   - 需要补充测试后才能通过

2. **Python 版本**
   - CI 使用 Python 3.11
   - 本地建议使用相同版本

3. **测试执行时间**
   - Auth Service: ~5s
   - User Service: ~1s
   - Order Service: ~0.3s
   - Payment Service: ~0.4s
   - Review Service: ~0.2s
   - Notification Service: ~0.2s

4. **首次运行**
   - 首次运行需要下载依赖（无缓存）
   - 后续运行会使用缓存，速度更快

---

## 🔄 工作流程图

```
Push 到 reid 分支
         ↓
    触发 CI 工作流
         ↓
    ┌─────────────┐
    │ Detect Path │
    │   Changes   │
    └─────────────┘
         ↓
    ┌─────────────────────────────┐
    │   并行运行 6 个服务测试      │
    ├─────────────────────────────┤
    │ • auth-service              │
    │ • user-service              │
    │ • order-service             │
    │ • payment-service           │
    │ • review-service            │
    │ • notification-service      │
    └─────────────────────────────┘
         ↓
    ┌─────────────┐
    │ 生成覆盖率   │
    │   报告      │
    └─────────────┘
         ↓
    ┌─────────────┐
    │ 上传到      │
    │ Artifacts   │
    └─────────────┘
         ↓
    ┌─────────────┐
    │ 验证结果    │
    │ 通过/失败   │
    └─────────────┘
```

---

## 📚 相关文档

- **单元测试参考**: `UNIT_TEST_REFERENCE.md`
- **覆盖率报告**: `COVERAGE_REPORT_SUMMARY.md`
- **英文版本**:
  - `ENG-UNIT_TEST_REFERENCE.md`
  - `ENG-COVERAGE_REPORT_SUMMARY.md`

---

**状态**: ✅ 已配置并可使用  
**下次更新**: 根据需要调整覆盖率阈值或添加新服务
