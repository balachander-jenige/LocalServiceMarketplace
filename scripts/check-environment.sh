#!/bin/bash
# 检查环境状态 / Check environment status

echo "🔍 检查环境状态... / Checking environment status..."
echo ""

# 检查云端服务 / Check cloud services
echo "☁️  云端服务状态 / Cloud Services Status:"

# 检查 AWS RDS MySQL / Check AWS RDS MySQL
echo -n "   🌐 AWS RDS MySQL: "
if mysql -h freelancer-db.c1ie6ii2q3oy.ap-southeast-1.rds.amazonaws.com -u freelancer -ppassword123 -e "SELECT 1" > /dev/null 2>&1; then
    echo "✅ 连接成功 / Connected"
else
    echo "❌ 连接失败 / Connection failed"
fi

# 检查 MongoDB Atlas / Check MongoDB Atlas
echo -n "   🌐 MongoDB Atlas: "
# 注意：你需要提供实际的 MongoDB Atlas 连接字符串 / Note: You need to provide actual MongoDB Atlas connection string
MONGODB_URL="mongodb+srv://freelancer:Password123@freelancer-cluster.rhf5ws4.mongodb.net/"
if mongosh "$MONGODB_URL" --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ 连接成功 / Connected"
else
    echo "❌ 连接失败或需要配置连接字符串 / Connection failed or connection string needs configuration"
fi

echo ""

# 检查本地服务 / Check local services
echo "🏠 本地服务状态 / Local Services Status:"

# 检查 Docker / Check Docker
echo -n "   🐳 Docker: "
if docker info > /dev/null 2>&1; then
    echo "✅ 运行中 / Running"
else
    echo "❌ 未运行 / Not running"
    exit 1
fi

# 检查 Redis / Check Redis
echo -n "   📦 Redis: "
if docker exec freelancer-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ 运行正常 / Running"
else
    echo "❌ 未运行 / Not running"
fi

# 检查 RabbitMQ / Check RabbitMQ
echo -n "   📦 RabbitMQ: "
if curl -s http://localhost:15672 > /dev/null 2>&1; then
    echo "✅ 运行正常 / Running"
else
    echo "❌ 未运行 / Not running"
fi

echo ""
echo "💡 如果本地服务未运行，执行: ./scripts/start-services.sh"
echo "💡 If local services are not running, execute: ./scripts/start-services.sh"