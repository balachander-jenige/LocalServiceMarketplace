#!/bin/bash
# 启动基础服务 / Start infrastructure services

set -e  # 遇到错误立即退出 / Exit on error

echo "🚀 启动基础服务... / Starting infrastructure services..."
echo "📍 数据库配置: MongoDB Atlas + AWS RDS / Database config: MongoDB Atlas + AWS RDS"
echo "🔧 本地服务: Redis + RabbitMQ / Local services: Redis + RabbitMQ"
echo ""

# 检查 Docker 是否运行 / Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker / Docker is not running, please start Docker first"
    exit 1
fi

# 检查 infrastructure 目录 / Check infrastructure directory
if [ ! -f "infrastructure/docker-compose.yml" ]; then
    echo "❌ 找不到 infrastructure/docker-compose.yml 文件"
    echo "❌ Cannot find infrastructure/docker-compose.yml file"
    echo "📁 请确保在项目根目录运行此脚本 / Please run this script from project root directory"
    exit 1
fi

# 停止已存在的容器 / Stop existing containers
echo "🛑 停止已存在的容器... / Stopping existing containers..."
docker-compose -f infrastructure/docker-compose.yml down > /dev/null 2>&1 || true

# 启动基础设施服务 / Start infrastructure services
echo "📦 启动 Redis + RabbitMQ... / Starting Redis + RabbitMQ..."
docker-compose -f infrastructure/docker-compose.yml up -d freelancer-redis freelancer-rabbitmq

# 等待服务启动 / Wait for services to start
echo "⏳ 等待服务启动... / Waiting for services to start..."
sleep 10

# 验证服务 / Verify services
echo ""
echo "🔍 验证服务状态... / Verifying service status..."

# 验证 Redis / Verify Redis
echo -n "📦 Redis: "
if docker exec freelancer-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ 运行正常 / Running (localhost:6379)"
else
    echo "❌ 启动失败 / Failed"
fi

# 验证 RabbitMQ / Verify RabbitMQ
echo -n "📦 RabbitMQ: "
sleep 5  # RabbitMQ需要更多时间启动 / RabbitMQ needs more time to start
if curl -s http://localhost:15672 > /dev/null 2>&1; then
    echo "✅ 运行正常 / Running (localhost:5672)"
    echo "   🌐 管理界面 / Management UI: http://localhost:15672 (guest/guest)"
else
    echo "⏳ 正在启动... / Starting... (请等待1-2分钟 / Please wait 1-2 minutes)"
fi

echo ""
echo "🎉 基础服务启动完成! / Infrastructure services started!"
echo ""
echo "📋 服务地址 / Service URLs:"
echo "   ✅ Redis:     localhost:6379"
echo "   ✅ RabbitMQ:  localhost:5672"  
echo "   🔗 RabbitMQ Management: http://localhost:15672"
echo ""
echo "☁️  云端服务 / Cloud Services:"
echo "   🌐 MongoDB Atlas: cluster0.xxxxx.mongodb.net"
echo "   🌐 AWS RDS MySQL: freelancer-db.xxxxx.rds.amazonaws.com"
echo ""
echo "💡 使用 ./scripts/stop-services.sh 停止服务"
echo "💡 Use ./scripts/stop-services.sh to stop services"
echo "📝 查看日志: docker-compose -f infrastructure/docker-compose.yml logs -f"
echo "📝 View logs: docker-compose -f infrastructure/docker-compose.yml logs -f"