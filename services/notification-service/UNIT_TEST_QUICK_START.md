# Notification Service - Unit Test Quick Start ⚡

## 🚀 Quick Commands

### Run All Tests
```bash
cd services/notification-service
poetry run pytest src/notification_service/tests/unit/ -v
```

### Run with Coverage
```bash
poetry run pytest src/notification_service/tests/unit/ \
  --cov=notification_service.services \
  --cov=notification_service.dao \
  --cov=notification_service.core.config \
  --cov-report=html
```

### View Coverage Report
```bash
open htmlcov/index.html
```

---

## 📊 Current Status

- **Tests**: 38 ✅
- **Coverage**: 100% ✅
- **Time**: 0.18s ⚡
- **Status**: All Passing ✅

---

## 📁 Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_config.py` | 10 | 100% ✅ |
| `test_customer_inbox_dao.py` | 8 | 100% ✅ |
| `test_provider_inbox_dao.py` | 8 | 100% ✅ |
| `test_notification_service.py` | 12 | 100% ✅ |

---

## 🎯 Test Categories

### Core (10 tests)
```bash
poetry run pytest src/notification_service/tests/unit/test_core/ -v
```

### DAO (16 tests)
```bash
poetry run pytest src/notification_service/tests/unit/test_dao/ -v
```

### Services (12 tests)
```bash
poetry run pytest src/notification_service/tests/unit/test_services/ -v
```

---

## 💡 Common Patterns

### Test a Specific File
```bash
poetry run pytest src/notification_service/tests/unit/test_services/test_notification_service.py -v
```

### Test a Specific Function
```bash
poetry run pytest src/notification_service/tests/unit/test_services/test_notification_service.py::TestNotificationServiceSendCustomer::test_send_customer_notification_success -v
```

### Run in Watch Mode (requires pytest-watch)
```bash
ptw src/notification_service/tests/unit/
```

---

## 🔧 Setup (First Time Only)

```bash
# Install dependencies
poetry install

# Verify setup
poetry run pytest src/notification_service/tests/unit/ -v
```

---

## 📈 Coverage Breakdown

| Module | Coverage |
|--------|----------|
| config.py | 100% ✅ |
| customer_inbox_dao.py | 100% ✅ |
| provider_inbox_dao.py | 100% ✅ |
| notification_service.py | 100% ✅ |

---

For detailed documentation, see [TEST_SUMMARY.md](./TEST_SUMMARY.md)
