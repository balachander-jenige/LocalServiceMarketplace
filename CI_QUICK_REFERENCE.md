# GitHub Actions CI 快速参考

## 📋 已创建的文件

### 工作流文件
- `.github/workflows/backend-lint.yml` - 代码质量检查（Black, isort, Flake8）
- `.github/workflows/backend-sast.yml` - 安全扫描（Bandit）

### 配置文件
- `.flake8` - Flake8 代码风格配置
- `pyproject.toml` - Black 和 isort 配置

## 🚀 触发条件

当前配置为**仅在 `reid` 分支**触发：
- ✅ Push 到 `reid` 分支时自动运行
- ✅ 向 `reid` 分支提交 Pull Request 时运行
- ✅ 支持手动触发（workflow_dispatch）
- ✅ 仅当 Python 文件变化时才运行（节省资源）

## 🔧 当前模式：报告模式（Report-Only）

**重要特性**：
- 所有检查都设置了 `continue-on-error: true`
- 检查失败**不会阻塞**代码提交
- 只是报告问题，方便你调整代码风格

## 📊 检查项目说明

### backend-lint.yml
| 工具 | 检查内容 | 作用 |
|------|---------|------|
| **Black** | 代码格式化 | 统一代码风格，行长度 120 |
| **isort** | 导入语句排序 | 自动整理 import 顺序 |
| **Flake8** | 代码风格 | PEP 8 规范检查 |

### backend-sast.yml
| 工具 | 检查内容 | 作用 |
|------|---------|------|
| **Bandit** | 安全漏洞扫描 | 检测常见安全问题 |

## 🧪 测试工作流

### 方法 1：自动触发
```bash
# 修改任意 Python 文件并提交到 reid 分支
git add .
git commit -m "test: trigger CI workflow"
git push origin reid
```

### 方法 2：手动触发
1. 访问 GitHub 仓库页面
2. 点击 **Actions** 标签
3. 选择工作流（Backend Linting 或 Backend Security Scan）
4. 点击 **Run workflow** 按钮

## 📈 查看结果

### GitHub Actions 页面
1. 访问：`https://github.com/daqiwu/ms-freelancer/actions`
2. 查看最近的工作流运行记录
3. 点击进入查看详细日志

### 安全报告下载
- Bandit 生成的 JSON 报告会自动上传
- 在 Actions 运行页面的 **Artifacts** 部分下载
- 保留 30 天

## 🎯 下一步行动

### 短期（1-2 周）- 测试阶段
1. ✅ 观察工作流运行情况
2. ✅ 根据报告调整代码风格
3. ✅ 确认没有误报或过多噪音
4. ✅ 记录执行时间（目标 < 3 分钟）

### 中期（2-4 周）- 强制模式
当测试稳定后，移除 `continue-on-error: true`：
```yaml
# 从这样（报告模式）
- name: Run Black
  run: black --check ...
  continue-on-error: true

# 改为这样（强制模式）
- name: Run Black
  run: black --check ...
  # 移除 continue-on-error，失败会阻塞
```

### 长期（4+ 周）- 扩展到团队
扩展触发分支到 `develop` 或 `dev`：
```yaml
on:
  push:
    branches:
      - reid
      - develop  # 添加团队开发分支
```

## 🛠️ 本地运行检查

在提交前本地运行相同的检查：

```bash
# 安装工具（在你的 backend-py3.13 环境中）
pip install black==24.4.2 isort==5.13.2 flake8==7.0.0 bandit==1.7.8

# 运行 Black（格式化 - 会修改文件）
black --line-length 120 services/ gateway-service/ shared/

# 运行 isort（排序导入 - 会修改文件）
isort --profile black --line-length 120 services/ gateway-service/ shared/

# 运行 Flake8（风格检查 - 只读）
flake8 services/ gateway-service/ shared/

# 运行 Bandit（安全扫描 - 只读）
# 只扫描 High 级别的安全问题（推荐用于初期测试）
bandit -r services/ gateway-service/ shared/ \
  --exclude '*/tests/*,*/alembic/versions/*' \
  --severity-level high

# 或者扫描 Medium 及以上级别（更严格）
# bandit -r services/ gateway-service/ shared/ \
#   --exclude '*/tests/*,*/alembic/versions/*' \
#   --severity-level medium
```

### 关于 Flake8 F401 警告（未使用的导入）

当前配置已设置为**忽略 API 文件中的未使用导入**，因为：
- 有些导入是为了保持 API 接口的完整性
- 有些导入是为了类型提示，即使代码中未直接使用
- 过度严格的规则会影响开发效率

如果你想完全清理这些警告，可以手动移除未使用的导入，或者运行：
```bash
# 查看所有 F401 错误
flake8 services/ gateway-service/ shared/ | grep F401
```

## 📝 忽略特定问题

### Flake8 忽略单行
```python
# 在代码行末添加 # noqa: E501
very_long_line_that_exceeds_120_characters = "some value"  # noqa: E501
```

### Bandit 忽略单行
```python
# 在代码行上方添加 # nosec
password = input("Enter password: ")  # nosec B106
```

## 🔄 快速回滚

如果遇到问题需要临时禁用：

### 方法 1：注释掉 workflow name
```yaml
# name: Backend Linting (DISABLED)
```

### 方法 2：只保留手动触发
```yaml
on:
  workflow_dispatch:  # 只允许手动触发
  # 注释掉 push 和 pull_request
```

## ⚙️ 配置调整建议

### 更宽松的 Flake8 规则
编辑 `.flake8`，添加更多忽略项：
```ini
extend-ignore = E203, W503, E501, E402, F401
```

### 更严格的 Black 格式
编辑 `pyproject.toml`，减少行长度：
```toml
[tool.black]
line-length = 100  # 从 120 改为 100
```

## 📞 问题排查

### 工作流没有触发？
- ✅ 确认推送到 `reid` 分支
- ✅ 确认修改了 Python 文件
- ✅ 检查 `.github/workflows/` 文件是否在 `reid` 分支上

### 工作流失败？
- ✅ 检查是否是预期的（当前是报告模式，失败不影响）
- ✅ 查看详细日志定位问题
- ✅ 在本地运行相同命令复现问题

### 执行时间太长？
- ✅ 检查是否安装了不必要的依赖
- ✅ 考虑启用 pip cache（已配置）
- ✅ 减少扫描范围（调整 paths 配置）

## 📚 工具文档

- [Black](https://black.readthedocs.io/)
- [isort](https://pycqa.github.io/isort/)
- [Flake8](https://flake8.pycqa.org/)
- [Bandit](https://bandit.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**创建时间**: 2025-10-22  
**当前模式**: 报告模式（Reid 分支测试）  
**预期完成**: 2-4 周后扩展到团队
