## 环境设置 / Environment Setup

### 启动基础服务 / Start Infrastructure Services

```bash
# 启动 Redis、RabbitMQ 等基础服务 / Start Redis, RabbitMQ and other infrastructure services
./scripts/start-services.sh

# 检查所有服务状态 / Check all service status
./scripts/check-environment.sh

# 停止所有本地服务 / Stop all local services
./scripts/stop-services.sh

# 查看服务日志 / View service logs
make logs