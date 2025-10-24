#!/bin/bash
# 重新生成所有服务的核心覆盖率报告

cd /Users/reidwu/Documents/ms-freelancer

echo "🔄 重新生成所有服务的核心覆盖率报告..."
echo ""

# Auth Service
echo "📦 Auth Service..."
cd services/auth-service
poetry run pytest src/auth_service/tests/unit/ -q \
  --cov=auth_service.core.security \
  --cov=auth_service.dao \
  --cov=auth_service.services \
  --cov-report=html 2>&1 | tail -5
cd ../..

# User Service
echo "📦 User Service..."
cd services/user-service
poetry run pytest src/user_service/tests/unit/ -q \
  --cov=user_service.core.config \
  --cov=user_service.dao \
  --cov=user_service.services \
  --cov-report=html 2>&1 | tail -5
cd ../..

# Order Service
echo "📦 Order Service..."
cd services/order-service
poetry run pytest src/order_service/tests/unit/ -q \
  --cov=order_service.core.config \
  --cov=order_service.services \
  --cov-report=html 2>&1 | tail -5
cd ../..

# Payment Service
echo "📦 Payment Service..."
cd services/payment-service
poetry run pytest src/payment_service/tests/unit/ -q \
  --cov=payment_service.core.config \
  --cov=payment_service.dao.payment_dao \
  --cov=payment_service.services \
  --cov-report=html 2>&1 | tail -5
cd ../..

# Review Service
echo "📦 Review Service..."
cd services/review-service
poetry run pytest src/review_service/tests/unit/ -q \
  --cov=review_service.core.config \
  --cov=review_service.dao \
  --cov=review_service.services \
  --cov-report=html 2>&1 | tail -5
cd ../..

# Notification Service
echo "📦 Notification Service..."
cd services/notification-service
poetry run pytest src/notification_service/tests/unit/ -q \
  --cov=notification_service.core.config \
  --cov=notification_service.dao \
  --cov=notification_service.services \
  --cov-report=html 2>&1 | tail -5
cd ../..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 所有覆盖率报告已重新生成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 查看报告："
echo "   open services/*/htmlcov/index.html"
echo ""
echo "或单独打开："
echo "   open services/auth-service/htmlcov/index.html"
echo "   open services/user-service/htmlcov/index.html"
echo "   open services/order-service/htmlcov/index.html"
echo "   open services/payment-service/htmlcov/index.html"
echo "   open services/review-service/htmlcov/index.html"
echo "   open services/notification-service/htmlcov/index.html"