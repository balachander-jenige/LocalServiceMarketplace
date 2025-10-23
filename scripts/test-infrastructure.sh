#!/bin/bash
# 测试基础设施启动和关闭脚本 / Test infrastructure startup and shutdown scripts

set -e

echo "🧪 测试基础设施脚本... / Testing infrastructure scripts..."
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试结果
TESTS_PASSED=0
TESTS_FAILED=0

test_passed() {
    echo -e "${GREEN}✅ $1${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_failed() {
    echo -e "${RED}❌ $1${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# 1. 测试启动脚本
echo "📋 测试 1: 启动脚本 / Test 1: Startup script"
echo ""

if [ ! -f "scripts/start-services.sh" ]; then
    test_failed "启动脚本不存在 / Startup script does not exist"
    exit 1
fi

echo "执行启动脚本... / Executing startup script..."
./scripts/start-services.sh

echo ""
echo "等待服务完全启动... / Waiting for services to fully start..."
sleep 15

# 2. 验证 Redis
echo ""
echo "📋 测试 2: Redis 连接 / Test 2: Redis connection"
if docker exec freelancer-redis redis-cli ping > /dev/null 2>&1; then
    test_passed "Redis 连接成功 / Redis connection successful"
else
    test_failed "Redis 连接失败 / Redis connection failed"
fi

# 测试 Redis 读写
echo -n "测试 Redis 读写... / Testing Redis read/write..."
if docker exec freelancer-redis redis-cli set test_key "test_value" > /dev/null 2>&1 && \
   [ "$(docker exec freelancer-redis redis-cli get test_key)" = "test_value" ]; then
    docker exec freelancer-redis redis-cli del test_key > /dev/null 2>&1
    test_passed "Redis 读写正常 / Redis read/write successful"
else
    test_failed "Redis 读写失败 / Redis read/write failed"
fi

# 3. 验证 RabbitMQ
echo ""
echo "📋 测试 3: RabbitMQ 连接 / Test 3: RabbitMQ connection"

# 等待 RabbitMQ 完全启动
sleep 10

if curl -s -u guest:guest http://localhost:15672/api/overview > /dev/null 2>&1; then
    test_passed "RabbitMQ API 访问成功 / RabbitMQ API access successful"
else
    test_failed "RabbitMQ API 访问失败 / RabbitMQ API access failed"
fi

# 4. 检查容器状态
echo ""
echo "📋 测试 4: 容器状态 / Test 4: Container status"

if docker ps | grep -q "freelancer-redis"; then
    test_passed "Redis 容器运行中 / Redis container running"
else
    test_failed "Redis 容器未运行 / Redis container not running"
fi

if docker ps | grep -q "freelancer-rabbitmq"; then
    test_passed "RabbitMQ 容器运行中 / RabbitMQ container running"
else
    test_failed "RabbitMQ 容器未运行 / RabbitMQ container not running"
fi

# 5. 测试停止脚本
echo ""
echo "📋 测试 5: 停止脚本 / Test 5: Shutdown script"
echo ""

if [ ! -f "scripts/stop-services.sh" ]; then
    test_failed "停止脚本不存在 / Shutdown script does not exist"
    exit 1
fi

echo "执行停止脚本... / Executing shutdown script..."
./scripts/stop-services.sh

echo ""
echo "等待容器完全停止... / Waiting for containers to fully stop..."
sleep 5

# 6. 验证服务已停止
echo ""
echo "📋 测试 6: 服务停止验证 / Test 6: Service shutdown verification"

if ! docker ps | grep -q "freelancer-redis"; then
    test_passed "Redis 容器已停止 / Redis container stopped"
else
    test_failed "Redis 容器仍在运行 / Redis container still running"
fi

if ! docker ps | grep -q "freelancer-rabbitmq"; then
    test_passed "RabbitMQ 容器已停止 / RabbitMQ container stopped"
else
    test_failed "RabbitMQ 容器仍在运行 / RabbitMQ container still running"
fi

# 7. 测试数据持久化
echo ""
echo "📋 测试 7: 数据持久化 / Test 7: Data persistence"

# 重新启动服务
echo "重新启动服务以测试数据持久化... / Restarting services to test data persistence..."
./scripts/start-services.sh
sleep 15

# 在 Redis 中写入测试数据
echo "写入测试数据... / Writing test data..."
docker exec freelancer-redis redis-cli set persist_test "data_persisted" > /dev/null 2>&1

# 停止服务
./scripts/stop-services.sh
sleep 5

# 再次启动
./scripts/start-services.sh
sleep 15

# 检查数据是否持久化
if [ "$(docker exec freelancer-redis redis-cli get persist_test 2>/dev/null)" = "data_persisted" ]; then
    test_passed "数据持久化成功 / Data persistence successful"
    docker exec freelancer-redis redis-cli del persist_test > /dev/null 2>&1
else
    test_failed "数据持久化失败 / Data persistence failed"
fi

# 最终清理
echo ""
echo "清理测试环境... / Cleaning up test environment..."
./scripts/stop-services.sh

# 总结
echo ""
echo "=========================================="
echo "📊 测试结果汇总 / Test Summary"
echo ""
echo -e "通过: ${GREEN}$TESTS_PASSED${NC} / Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "失败: ${RED}$TESTS_FAILED${NC} / Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过! 脚本运行正常! / All tests passed! Scripts are working correctly!${NC}"
    exit 0
else
    echo -e "${RED}❌ 部分测试失败，请检查脚本配置 / Some tests failed, please check script configuration${NC}"
    exit 1
fi