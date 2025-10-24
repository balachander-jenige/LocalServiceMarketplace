# Review Service Unit Tests - Quick Start Guide

## TL;DR - Run Tests Now! 🚀

```bash
cd /path/to/review-service

# Install dependencies (first time only)
poetry install

# Run all tests with coverage
poetry run pytest src/review_service/tests/unit/ -v \
  --cov=review_service.services \
  --cov=review_service.dao \
  --cov=review_service.core.config

# Expected output: 39 passed in 0.14s ✨ 100% coverage
```

## Common Commands

### Run All Tests
```bash
# Verbose output with coverage
poetry run pytest src/review_service/tests/unit/ -v \
  --cov=review_service.services \
  --cov=review_service.dao \
  --cov=review_service.core.config \
  --cov-report=term-missing
```

### Run by Category
```bash
# Core configuration tests (9 tests)
poetry run pytest src/review_service/tests/unit/test_core/ -v

# DAO layer tests (17 tests)
poetry run pytest src/review_service/tests/unit/test_dao/ -v

# Service layer tests (13 tests)
poetry run pytest src/review_service/tests/unit/test_services/ -v
```

### Run Specific Test File
```bash
# Config tests
poetry run pytest src/review_service/tests/unit/test_core/test_config.py -v

# ReviewDAO tests
poetry run pytest src/review_service/tests/unit/test_dao/test_review_dao.py -v

# RatingDAO tests
poetry run pytest src/review_service/tests/unit/test_dao/test_rating_dao.py -v

# ReviewService tests
poetry run pytest src/review_service/tests/unit/test_services/test_review_service.py -v
```

### Run Single Test
```bash
# Run specific test by name
poetry run pytest src/review_service/tests/unit/test_services/test_review_service.py::TestReviewServiceCreateReview::test_create_review_success -v

# Run tests matching pattern
poetry run pytest src/review_service/tests/unit/ -k "create_review" -v
```

### Run with Markers
```bash
# Run only DAO tests
poetry run pytest -m dao -v

# Run only service tests
poetry run pytest -m service -v

# Run only core tests
poetry run pytest -m core -v
```

### Coverage Reports
```bash
# Terminal report with missing lines
poetry run pytest src/review_service/tests/unit/ \
  --cov=review_service.services \
  --cov=review_service.dao \
  --cov=review_service.core.config \
  --cov-report=term-missing

# HTML report (opens in browser)
poetry run pytest src/review_service/tests/unit/ \
  --cov=review_service.services \
  --cov=review_service.dao \
  --cov=review_service.core.config \
  --cov-report=html && open htmlcov/index.html
```

### Debugging
```bash
# Show print statements (-s flag)
poetry run pytest src/review_service/tests/unit/test_services/test_review_service.py -v -s

# Stop at first failure (-x flag)
poetry run pytest src/review_service/tests/unit/ -v -x

# Show local variables on failure (--showlocals)
poetry run pytest src/review_service/tests/unit/ -v --showlocals

# Enter debugger on failure (--pdb)
poetry run pytest src/review_service/tests/unit/ -v --pdb
```

## Test Output Interpretation

### Success Output
```
======================== test session starts ========================
collected 39 items

test_config.py::TestSettings::test_settings_with_env_vars PASSED [  2%]
test_config.py::TestSettings::test_settings_default_values PASSED [  5%]
...
test_review_service.py::TestReviewServiceGetReviewByOrder::test_get_review_by_order_not_found PASSED [100%]

---------- coverage: platform darwin, python 3.13.3-final-0 ----------
Name                                            Stmts   Miss  Cover
--------------------------------------------------------------------
src/review_service/core/config.py                  14      0   100%
src/review_service/dao/rating_dao.py               15      0   100%
src/review_service/dao/review_dao.py               19      0   100%
src/review_service/services/review_service.py      34      0   100%
--------------------------------------------------------------------
TOTAL                                              87      0   100%

======================== 39 passed in 0.14s =========================
```

✅ **All tests pass** - 39/39 tests successful  
✅ **100% coverage** - All 87 statements covered  
✅ **Fast execution** - Completed in 0.14 seconds

### Failure Output
```
FAILED test_review_service.py::TestReviewServiceCreateReview::test_create_review_success - AssertionError: assert 4 == 5
```

❌ **Test failed** - Check assertion or mock setup  
🔍 **Debug**: Use `-v --showlocals` to see local variables  
🐛 **Fix**: Update test or fix implementation

## Test Structure

```
src/review_service/tests/unit/
├── conftest.py                         # Shared fixtures (9 fixtures)
├── test_core/
│   ├── __init__.py
│   └── test_config.py                  # Config tests (9 tests)
├── test_dao/
│   ├── __init__.py
│   ├── test_review_dao.py              # ReviewDAO tests (9 tests)
│   └── test_rating_dao.py              # RatingDAO tests (8 tests)
├── test_services/
│   ├── __init__.py
│   └── test_review_service.py          # ReviewService tests (13 tests)
├── TEST_SUMMARY.md                     # Detailed test documentation
├── UNIT_TEST_QUICK_START.md            # This file
└── UNIT_TEST_README.md                 # Comprehensive guide
```

## Quick Reference

### Test Counts
- **Core**: 9 tests (config.py)
- **DAO**: 17 tests (review_dao: 9, rating_dao: 8)
- **Service**: 13 tests (review_service.py)
- **Total**: 39 tests

### Coverage
- **config.py**: 100% (14 statements)
- **review_dao.py**: 100% (19 statements)
- **rating_dao.py**: 100% (15 statements)
- **review_service.py**: 100% (34 statements)
- **Overall**: 100% (87 statements)

### Execution Time
- **Average**: 0.14 seconds
- **Per test**: ~3.6ms
- **Platform**: macOS, Python 3.13.3

## Troubleshooting

### Tests Not Found
```bash
# Make sure you're in the correct directory
cd /path/to/review-service

# Verify pytest can discover tests
poetry run pytest --collect-only
```

### Import Errors
```bash
# Install dependencies
poetry install

# Verify Python environment
poetry env info

# Check if review_service module is installed
poetry run python -c "import review_service; print(review_service.__file__)"
```

### Coverage Issues
```bash
# Make sure coverage paths are correct
poetry run pytest src/review_service/tests/unit/ \
  --cov=review_service \
  --cov-report=term-missing

# Check which files are being tested
poetry run pytest --cov=review_service --cov-report=html
open htmlcov/index.html
```

### Async Test Failures
```bash
# Verify pytest-asyncio is installed
poetry show pytest-asyncio

# Check pytest.ini has asyncio_mode=auto
cat pytest.ini | grep asyncio_mode

# Run with explicit asyncio mode
poetry run pytest --asyncio-mode=auto -v
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Review Service Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: |
          poetry run pytest src/review_service/tests/unit/ -v \
            --cov=review_service.services \
            --cov=review_service.dao \
            --cov=review_service.core.config \
            --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hook
```bash
# Add to .git/hooks/pre-commit
#!/bin/sh
cd services/review-service
poetry run pytest src/review_service/tests/unit/ --cov=review_service -q
```

## Next Steps

1. **Run tests**: `poetry run pytest src/review_service/tests/unit/ -v`
2. **Check coverage**: Add `--cov-report=html` to see detailed coverage
3. **Read details**: See `TEST_SUMMARY.md` for comprehensive test documentation
4. **Add new tests**: Follow patterns in existing test files
5. **Maintain 100%**: Keep coverage at 100% for core modules

## Key Takeaways

- 🎯 **39 tests** provide comprehensive coverage
- ⚡ **0.14s execution** - fast feedback loop
- 🏆 **100% coverage** - all core logic tested
- 📚 **Well-structured** - easy to navigate and extend
- 🔧 **Easy to run** - one command to verify everything

Happy testing! 🚀✨
