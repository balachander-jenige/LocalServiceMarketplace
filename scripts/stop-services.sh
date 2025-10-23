#!/bin/bash
# 停止基础服务 / Stop infrastructure services

echo "🛑 停止基础服务... / Stopping infrastructure services..."

# 检查 docker-compose 文件是否存在 / Check if docker-compose file exists
if [ ! -f "infrastructure/docker-compose.yml" ]; then
    echo "❌ 找不到 infrastructure/docker-compose.yml 文件"
    echo "❌ Cannot find infrastructure/docker-compose.yml file"
    exit 1
fi

# 停止并删除容器 / Stop and remove containers
docker-compose -f infrastructure/docker-compose.yml down

echo ""
echo "✅ 基础服务已停止 / Infrastructure services stopped"
echo "💾 数据已保留在 Docker volumes 中 / Data preserved in Docker volumes"
echo ""
echo "🔧 其他操作 / Other operations:"
echo "   🗑️  清理所有数据 / Clean all data:"
echo "      docker-compose -f infrastructure/docker-compose.yml down -v"
echo "   📋 查看 volumes / View volumes:"
echo "      docker volume ls | grep freelancer"
echo "   🔄 重启服务 / Restart services:"
echo "      ./scripts/start-services.sh"