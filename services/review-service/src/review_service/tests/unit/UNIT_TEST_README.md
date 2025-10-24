# Review Service Unit Tests - Complete Guide

## Table of Contents
- [Overview](#overview)
- [Getting Started](#getting-started)
- [Test Architecture](#test-architecture)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Running Tests](#running-tests)
- [Coverage Analysis](#coverage-analysis)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

## Overview

This document provides comprehensive guidance for understanding, running, and maintaining the Review Service unit test suite.

### Test Statistics
- **Total Tests**: 39 tests
- **Coverage**: 100% (87 statements)
- **Execution Time**: 0.14 seconds
- **Platform**: Python 3.13.3, pytest 7.4.4

### Test Distribution
| Layer | Tests | Coverage | Files |
|-------|-------|----------|-------|
| Core | 9 | 100% | config.py |
| DAO | 17 | 100% | review_dao.py, rating_dao.py |
| Service | 13 | 100% | review_service.py |

## Getting Started

### Prerequisites
```bash
# Python 3.10+ required
python --version

# Poetry for dependency management
pip install poetry
```

### Installation
```bash
# Navigate to Review Service directory
cd services/review-service

# Install dependencies (including test dependencies)
poetry install

# Verify installation
poetry run pytest --version
```

### Quick Test Run
```bash
# Run all tests with coverage
poetry run pytest src/review_service/tests/unit/ -v \
  --cov=review_service.services \
  --cov=review_service.dao \
  --cov=review_service.core.config \
  --cov-report=term-missing

# Expected output: 39 passed in 0.14s, 100% coverage
```

## Test Architecture

### Directory Structure
```
src/review_service/tests/unit/
├── conftest.py                         # Shared fixtures and configuration
├── pytest.ini                          # Pytest configuration
├── test_core/                          # Core module tests
│   ├── __init__.py
│   └── test_config.py                  # Configuration tests (9 tests)
├── test_dao/                           # Data Access Object tests
│   ├── __init__.py
│   ├── test_review_dao.py              # ReviewDAO tests (9 tests)
│   └── test_rating_dao.py              # RatingDAO tests (8 tests)
├── test_services/                      # Business logic tests
│   ├── __init__.py
│   └── test_review_service.py          # ReviewService tests (13 tests)
└── docs/
    ├── TEST_SUMMARY.md                 # Test summary and results
    ├── UNIT_TEST_QUICK_START.md        # Quick reference guide
    └── UNIT_TEST_README.md             # This file
```

### pytest.ini Configuration
```ini
[tool:pytest]
testpaths = src/review_service/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

markers =
    unit: Unit tests
    dao: DAO layer tests
    service: Service layer tests
    core: Core configuration tests

addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
```

### conftest.py Fixtures

#### Database Mocks
```python
@pytest.fixture
def mock_db(mocker):
    """Mock AsyncIOMotorDatabase."""
    return mocker.MagicMock(spec=AsyncIOMotorDatabase)

@pytest.fixture
def mock_review_collection(mock_db):
    """Mock reviews collection."""
    collection = mocker.MagicMock()
    mock_db.__getitem__.return_value = collection
    return collection

@pytest.fixture
def mock_rating_collection(mock_db):
    """Mock provider_ratings collection."""
    collection = mocker.MagicMock()
    mock_db.__getitem__.return_value = collection
    return collection
```

#### DAO Fixtures
```python
@pytest.fixture
def review_dao(mock_db, mock_review_collection):
    """Create ReviewDAO instance with mocked database."""
    dao = ReviewDAO(mock_db)
    dao.collection = mock_review_collection
    return dao

@pytest.fixture
def rating_dao(mock_db, mock_rating_collection):
    """Create RatingDAO instance with mocked database."""
    dao = RatingDAO(mock_db)
    dao.collection = mock_rating_collection
    return dao
```

#### Service Fixtures
```python
@pytest.fixture
def review_service(mock_db):
    """Create ReviewService instance with mocked database."""
    return ReviewService(mock_db)
```

#### Data Fixtures
```python
@pytest.fixture
def sample_review():
    """Sample review data for testing."""
    return {
        "order_id": 100,
        "customer_id": 1,
        "provider_id": 2,
        "stars": 5,
        "content": "Excellent service!",
        "created_at": datetime.now()
    }

@pytest.fixture
def sample_rating():
    """Sample rating data for testing."""
    return {
        "provider_id": 2,
        "average_rating": 4.5,
        "total_reviews": 10
    }
```

#### Mock Fixtures
```python
@pytest.fixture
def mock_event_publisher(mocker):
    """Mock EventPublisher for testing event publishing."""
    mock_publish_review_created = mocker.patch(
        "review_service.services.review_service.EventPublisher.publish_review_created",
        new_callable=AsyncMock
    )
    mock_publish_rating_updated = mocker.patch(
        "review_service.services.review_service.EventPublisher.publish_rating_updated",
        new_callable=AsyncMock
    )
    return {
        "publish_review_created": mock_publish_review_created,
        "publish_rating_updated": mock_publish_rating_updated
    }
```

## Test Categories

### 1. Core Configuration Tests (test_core/test_config.py)

**Purpose**: Validate application configuration and settings management.

**Coverage**: 100% (14 statements in config.py)

**Test Cases**:
1. **test_settings_with_env_vars** - Load configuration from environment variables
2. **test_settings_default_values** - Verify default values (SERVICE_NAME="review-service", PORT=8005)
3. **test_settings_required_fields** - Ensure required fields (MONGODB_URL, RABBITMQ_URL) raise ValidationError
4. **test_settings_mongodb_url_validation** - Validate MongoDB connection string format
5. **test_settings_rabbitmq_url_validation** - Validate RabbitMQ connection string format
6. **test_settings_service_port_type** - Verify SERVICE_PORT is integer type
7. **test_settings_service_urls_override** - Test overriding service URLs (AUTH, ORDER, USER)
8. **test_settings_log_level_values** - Test custom log levels (DEBUG, INFO, WARNING, ERROR)
9. **test_settings_service_name_custom** - Test custom service name override

**Example Test**:
```python
class TestSettings:
    def test_settings_with_env_vars(self, monkeypatch):
        """Test loading settings from environment variables."""
        monkeypatch.setenv("MONGODB_URL", "mongodb://test:27017/test_db")
        monkeypatch.setenv("RABBITMQ_URL", "amqp://guest:guest@test:5672/")
        monkeypatch.setenv("SERVICE_NAME", "custom-review-service")
        monkeypatch.setenv("SERVICE_PORT", "9000")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        settings = Settings()

        assert settings.MONGODB_URL == "mongodb://test:27017/test_db"
        assert settings.RABBITMQ_URL == "amqp://guest:guest@test:5672/"
        assert settings.SERVICE_NAME == "custom-review-service"
        assert settings.SERVICE_PORT == 9000
        assert settings.LOG_LEVEL == "DEBUG"
```

### 2. ReviewDAO Tests (test_dao/test_review_dao.py)

**Purpose**: Test ReviewDAO data access methods for review CRUD operations.

**Coverage**: 100% (19 statements in review_dao.py)

**Test Classes**:
- `TestReviewDAOCreate` (3 tests) - Review creation scenarios
- `TestReviewDAOGet` (6 tests) - Review retrieval scenarios

**Key Test Cases**:

#### TestReviewDAOCreate
1. **test_create_success** - Create review with all fields
```python
@pytest.mark.asyncio
async def test_create_success(self, review_dao, mock_review_collection, sample_review):
    """Test successfully creating a review."""
    mock_review_collection.insert_one = AsyncMock()
    
    review = await review_dao.create(Review(**sample_review))
    
    assert review.order_id == 100
    assert review.stars == 5
    mock_review_collection.insert_one.assert_called_once()
```

2. **test_create_with_all_fields** - Create with specific field values
3. **test_create_without_content** - Create with optional content=None

#### TestReviewDAOGet
1. **test_get_by_order_id_success** - Retrieve review by order ID
2. **test_get_by_order_id_not_found** - Handle non-existent order
3. **test_get_by_order_id_removes_mongodb_id** - Verify _id field removal
4. **test_get_reviews_for_provider_success** - Get all reviews for provider
5. **test_get_reviews_for_provider_empty** - Handle provider with no reviews
6. **test_get_reviews_for_provider_removes_mongodb_ids** - Verify bulk _id removal

**MongoDB _id Removal Pattern**:
```python
@pytest.mark.asyncio
async def test_get_by_order_id_removes_mongodb_id(self, review_dao, mock_review_collection):
    """Test that MongoDB _id field is removed from results."""
    mock_review_collection.find_one = AsyncMock(
        return_value={
            "_id": "mongo_id_should_be_removed",
            "order_id": 100,
            "customer_id": 1,
            "provider_id": 2,
            "stars": 5,
            "content": "Great!",
            "created_at": datetime.now()
        }
    )
    
    review = await review_dao.get_by_order_id(100)
    
    review_dict = review.model_dump()
    assert "_id" not in review_dict
```

### 3. RatingDAO Tests (test_dao/test_rating_dao.py)

**Purpose**: Test RatingDAO methods for provider rating management.

**Coverage**: 100% (15 statements in rating_dao.py)

**Test Classes**:
- `TestRatingDAOGet` (3 tests) - Rating retrieval
- `TestRatingDAOUpsert` (5 tests) - Rating upsert operations

**Key Test Cases**:

#### TestRatingDAOGet
1. **test_get_by_provider_id_success** - Get rating for provider
2. **test_get_by_provider_id_not_found** - Handle non-existent provider
3. **test_get_by_provider_id_removes_mongodb_id** - Verify _id removal

#### TestRatingDAOUpsert
1. **test_upsert_rating_new** - Create new rating (insert)
```python
@pytest.mark.asyncio
async def test_upsert_rating_new(self, rating_dao, mock_rating_collection):
    """Test upserting a new rating."""
    mock_rating_collection.update_one = AsyncMock()
    
    rating = await rating_dao.upsert_rating(
        provider_id=2,
        average_rating=4.5,
        total_reviews=10
    )
    
    assert rating.provider_id == 2
    assert rating.average_rating == 4.5
    assert rating.total_reviews == 10
    mock_rating_collection.update_one.assert_called_once_with(
        {"provider_id": 2},
        {"$set": {"average_rating": 4.5, "total_reviews": 10}},
        upsert=True
    )
```

2. **test_upsert_rating_update_existing** - Update existing rating
3. **test_upsert_rating_with_perfect_score** - Handle perfect 5.0 rating
4. **test_upsert_rating_with_low_score** - Handle low ratings (2.5)
5. **test_upsert_rating_incremental_update** - Incremental rating updates (5.0 → 4.5)

### 4. ReviewService Tests (test_services/test_review_service.py)

**Purpose**: Test ReviewService business logic and orchestration.

**Coverage**: 100% (34 statements in review_service.py)

**Test Classes**:
- `TestReviewServiceCreateReview` (8 tests) - Review creation workflow
- `TestReviewServiceGetProviderRating` (2 tests) - Rating retrieval
- `TestReviewServiceGetReviewsForProvider` (2 tests) - Review listing
- `TestReviewServiceGetReviewByOrder` (2 tests) - Single review retrieval

**Key Test Cases**:

#### TestReviewServiceCreateReview

**1. test_create_review_success** - Complete creation workflow
```python
@pytest.mark.asyncio
async def test_create_review_success(self, review_service, mock_event_publisher):
    """Test successfully creating a review."""
    # Mock ReviewDAO.create
    review_service.review_dao.create = AsyncMock(
        return_value=Review(
            order_id=100, customer_id=1, provider_id=2,
            stars=5, content="Excellent!", created_at=datetime.now()
        )
    )
    
    # Mock ReviewDAO.get_reviews_for_provider
    review_service.review_dao.get_reviews_for_provider = AsyncMock(
        return_value=[
            Review(order_id=100, customer_id=1, provider_id=2, stars=5, created_at=datetime.now()),
            Review(order_id=101, customer_id=2, provider_id=2, stars=4, created_at=datetime.now())
        ]
    )
    
    # Mock RatingDAO.upsert_rating
    review_service.rating_dao.upsert_rating = AsyncMock(
        return_value=ProviderRating(provider_id=2, average_rating=4.5, total_reviews=2)
    )
    
    # Act
    review_data = {
        "order_id": 100, "customer_id": 1, "provider_id": 2,
        "stars": 5, "content": "Excellent!"
    }
    review = await review_service.create_review(review_data)
    
    # Assert
    assert review.order_id == 100
    assert review.stars == 5
    review_service.review_dao.create.assert_called_once()
    review_service.rating_dao.upsert_rating.assert_called_once()
```

**2. test_create_review_without_content** - Handle optional content field

**3. test_create_review_publishes_review_created_event** - Verify event publishing
```python
@pytest.mark.asyncio
async def test_create_review_publishes_review_created_event(
    self, review_service, mock_event_publisher
):
    """Test that ReviewCreatedEvent is published."""
    # Setup mocks...
    
    review_data = {
        "order_id": 100, "customer_id": 1, "provider_id": 2,
        "stars": 5, "content": "Great!"
    }
    await review_service.create_review(review_data)
    
    # Verify both events published
    mock_event_publisher["publish_review_created"].assert_called_once()
    mock_event_publisher["publish_rating_updated"].assert_called_once()
```

**4. test_create_review_publishes_rating_updated_event** - Verify rating event

**5. test_create_review_calculates_average_rating** - Rating calculation
```python
@pytest.mark.asyncio
async def test_create_review_calculates_average_rating(
    self, review_service, mock_event_publisher
):
    """Test that average rating is calculated correctly."""
    review_service.review_dao.create = AsyncMock(...)
    review_service.review_dao.get_reviews_for_provider = AsyncMock(
        return_value=[
            Review(order_id=100, customer_id=1, provider_id=2, stars=5, ...),
            Review(order_id=101, customer_id=2, provider_id=2, stars=4, ...),
            Review(order_id=102, customer_id=3, provider_id=2, stars=3, ...)
        ]
    )
    review_service.rating_dao.upsert_rating = AsyncMock()
    
    review_data = {"order_id": 102, "customer_id": 3, "provider_id": 2, "stars": 3}
    await review_service.create_review(review_data)
    
    # Verify calculation: (5 + 4 + 3) / 3 = 4.0
    call_args = review_service.rating_dao.upsert_rating.call_args[0]
    assert call_args[1] == 4.0  # average_rating
    assert call_args[2] == 3    # total_reviews
```

**6. test_create_review_updates_rating_in_dao** - DAO interaction

**7. test_create_review_with_multiple_reviews** - Multiple reviews scenario
```python
# Tests rating with 5 reviews: (5+4+3+5+2)/5 = 3.8
```

#### TestReviewServiceGetProviderRating
1. **test_get_provider_rating_success** - Get existing rating
2. **test_get_provider_rating_returns_default_when_not_found** - Default rating (5.0, 0)

#### TestReviewServiceGetReviewsForProvider
1. **test_get_reviews_for_provider_success** - Get reviews list
2. **test_get_reviews_for_provider_empty** - Empty reviews list

#### TestReviewServiceGetReviewByOrder
1. **test_get_review_by_order_success** - Get review by order
2. **test_get_review_by_order_not_found** - Handle non-existent order

## Writing Tests

### Test Template - DAO Layer
```python
"""Tests for ReviewDAO."""

from unittest.mock import AsyncMock
import pytest
from review_service.models.review import Review

class TestReviewDAOYourMethod:
    """Test ReviewDAO.your_method."""
    
    @pytest.mark.asyncio
    async def test_your_method_success(self, review_dao, mock_review_collection):
        """Test successful scenario."""
        # Arrange - Setup mocks
        mock_review_collection.your_method = AsyncMock(
            return_value={"order_id": 100, "stars": 5, ...}
        )
        
        # Act - Call the method
        result = await review_dao.your_method(100)
        
        # Assert - Verify results
        assert result is not None
        assert result.order_id == 100
        mock_review_collection.your_method.assert_called_once_with({"order_id": 100})
    
    @pytest.mark.asyncio
    async def test_your_method_not_found(self, review_dao, mock_review_collection):
        """Test not found scenario."""
        mock_review_collection.your_method = AsyncMock(return_value=None)
        
        result = await review_dao.your_method(999)
        
        assert result is None
```

### Test Template - Service Layer
```python
"""Tests for ReviewService."""

from unittest.mock import AsyncMock
import pytest
from review_service.models.review import Review

class TestReviewServiceYourMethod:
    """Test ReviewService.your_method."""
    
    @pytest.mark.asyncio
    async def test_your_method_success(self, review_service, mock_event_publisher):
        """Test successful scenario."""
        # Arrange - Mock dependencies
        review_service.review_dao.some_method = AsyncMock(
            return_value=Review(order_id=100, ...)
        )
        review_service.rating_dao.another_method = AsyncMock(...)
        
        # Act
        result = await review_service.your_method(100)
        
        # Assert
        assert result.order_id == 100
        review_service.review_dao.some_method.assert_called_once()
        mock_event_publisher["publish_review_created"].assert_called_once()
```

### AAA Pattern (Arrange-Act-Assert)

All tests follow the AAA pattern for clarity and maintainability:

```python
@pytest.mark.asyncio
async def test_example(self, review_service):
    # ======== ARRANGE ========
    # Set up test data and mock behavior
    review_service.review_dao.create = AsyncMock(
        return_value=Review(order_id=100, stars=5, ...)
    )
    review_data = {"order_id": 100, "stars": 5}
    
    # ======== ACT ========
    # Execute the method under test
    result = await review_service.create_review(review_data)
    
    # ======== ASSERT ========
    # Verify expected outcomes
    assert result.order_id == 100
    assert result.stars == 5
    review_service.review_dao.create.assert_called_once()
```

### Async Testing Guidelines

**1. Use @pytest.mark.asyncio decorator**
```python
@pytest.mark.asyncio
async def test_async_method(self, review_dao):
    result = await review_dao.get_by_order_id(100)
    assert result is not None
```

**2. Use AsyncMock for async methods**
```python
from unittest.mock import AsyncMock

mock_collection.find_one = AsyncMock(return_value={...})
```

**3. Configure pytest.ini**
```ini
asyncio_mode = auto
```

### Mock Strategy

**DAO Tests - Mock MongoDB Collections**
```python
@pytest.mark.asyncio
async def test_dao_method(self, review_dao, mock_review_collection):
    # Mock collection method directly
    mock_review_collection.find_one = AsyncMock(return_value={...})
    
    result = await review_dao.get_by_order_id(100)
    
    mock_review_collection.find_one.assert_called_once_with({"order_id": 100})
```

**Service Tests - Mock DAO Methods**
```python
@pytest.mark.asyncio
async def test_service_method(self, review_service):
    # Mock DAO methods, not MongoDB collections
    review_service.review_dao.create = AsyncMock(return_value=...)
    review_service.rating_dao.upsert_rating = AsyncMock(return_value=...)
    
    result = await review_service.create_review(review_data)
    
    review_service.review_dao.create.assert_called_once()
```

**Event Publisher Mocking**
```python
@pytest.fixture
def mock_event_publisher(mocker):
    """Mock EventPublisher."""
    mock_review_created = mocker.patch(
        "review_service.services.review_service.EventPublisher.publish_review_created",
        new_callable=AsyncMock
    )
    mock_rating_updated = mocker.patch(
        "review_service.services.review_service.EventPublisher.publish_rating_updated",
        new_callable=AsyncMock
    )
    return {
        "publish_review_created": mock_review_created,
        "publish_rating_updated": mock_rating_updated
    }
```

### MongoDB _id Removal Testing

All DAO tests should verify that MongoDB's `_id` field is removed:

```python
@pytest.mark.asyncio
async def test_removes_mongodb_id(self, review_dao, mock_review_collection):
    """Test that MongoDB _id field is removed from results."""
    mock_review_collection.find_one = AsyncMock(
        return_value={
            "_id": "should_be_removed",
            "order_id": 100,
            "stars": 5,
            ...
        }
    )
    
    result = await review_dao.get_by_order_id(100)
    
    result_dict = result.model_dump()
    assert "_id" not in result_dict  # Key assertion
```

## Running Tests

### Basic Commands

**Run all tests**
```bash
poetry run pytest src/review_service/tests/unit/ -v
```

**Run with coverage**
```bash
poetry run pytest src/review_service/tests/unit/ -v \
  --cov=review_service.services \
  --cov=review_service.dao \
  --cov=review_service.core.config \
  --cov-report=term-missing
```

### Run by Category

**Core tests**
```bash
poetry run pytest src/review_service/tests/unit/test_core/ -v
```

**DAO tests**
```bash
poetry run pytest src/review_service/tests/unit/test_dao/ -v
```

**Service tests**
```bash
poetry run pytest src/review_service/tests/unit/test_services/ -v
```

### Run Specific Tests

**Single file**
```bash
poetry run pytest src/review_service/tests/unit/test_services/test_review_service.py -v
```

**Single test class**
```bash
poetry run pytest src/review_service/tests/unit/test_services/test_review_service.py::TestReviewServiceCreateReview -v
```

**Single test method**
```bash
poetry run pytest src/review_service/tests/unit/test_services/test_review_service.py::TestReviewServiceCreateReview::test_create_review_success -v
```

**Tests matching pattern**
```bash
# Run all tests with "rating" in the name
poetry run pytest src/review_service/tests/unit/ -k "rating" -v

# Run all create tests
poetry run pytest src/review_service/tests/unit/ -k "create" -v
```

### Run with Markers

**Run only DAO tests**
```bash
poetry run pytest -m dao -v
```

**Run only service tests**
```bash
poetry run pytest -m service -v
```

**Run only core tests**
```bash
poetry run pytest -m core -v
```

### Debugging Options

**Show print statements**
```bash
poetry run pytest src/review_service/tests/unit/ -v -s
```

**Stop at first failure**
```bash
poetry run pytest src/review_service/tests/unit/ -v -x
```

**Show local variables on failure**
```bash
poetry run pytest src/review_service/tests/unit/ -v --showlocals
```

**Enter debugger on failure**
```bash
poetry run pytest src/review_service/tests/unit/ -v --pdb
```

**Verbose output with traceback**
```bash
poetry run pytest src/review_service/tests/unit/ -vv --tb=long
```

## Coverage Analysis

### Generate Coverage Report

**Terminal report**
```bash
poetry run pytest src/review_service/tests/unit/ \
  --cov=review_service \
  --cov-report=term-missing
```

**HTML report**
```bash
poetry run pytest src/review_service/tests/unit/ \
  --cov=review_service \
  --cov-report=html

# Open in browser
open htmlcov/index.html
```

**XML report (for CI/CD)**
```bash
poetry run pytest src/review_service/tests/unit/ \
  --cov=review_service \
  --cov-report=xml
```

### Coverage Output Interpretation

```
---------- coverage: platform darwin, python 3.13.3-final-0 ----------
Name                                            Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------------
src/review_service/core/config.py                  14      0   100%
src/review_service/dao/rating_dao.py               15      0   100%
src/review_service/dao/review_dao.py               19      0   100%
src/review_service/services/review_service.py      34      0   100%
-----------------------------------------------------------------------------
TOTAL                                              87      0   100%
```

- **Stmts**: Total number of executable statements
- **Miss**: Number of statements not covered by tests
- **Cover**: Coverage percentage
- **Missing**: Line numbers of uncovered statements (if any)

### Coverage Goals

- **Core modules** (services, dao, config): 100% coverage ✅
- **Event models**: Not required (simple data classes)
- **API routes**: Covered by integration tests
- **Overall target**: Maintain 100% for core business logic

## Best Practices

### 1. Test Independence
- Each test should be independent and runnable in isolation
- Use fixtures to set up clean test environment
- Don't rely on test execution order

```python
# Good - Independent test
@pytest.mark.asyncio
async def test_get_rating(self, rating_dao, mock_rating_collection):
    mock_rating_collection.find_one = AsyncMock(return_value={...})
    result = await rating_dao.get_by_provider_id(1)
    assert result is not None

# Bad - Depends on previous test state
@pytest.mark.asyncio
async def test_get_rating_after_create(self, rating_dao):
    # Assumes rating was created in previous test
    result = await rating_dao.get_by_provider_id(1)
    assert result is not None
```

### 2. Clear Test Names
Test names should describe what is being tested and expected outcome:

```python
# Good - Descriptive names
def test_create_review_success()
def test_get_by_order_id_not_found()
def test_upsert_rating_with_perfect_score()

# Bad - Unclear names
def test_review_1()
def test_get()
def test_rating()
```

### 3. One Assertion Per Concept
Focus each test on one specific behavior or outcome:

```python
# Good - Focused test
@pytest.mark.asyncio
async def test_get_by_order_id_removes_mongodb_id(self, review_dao, mock_review_collection):
    """Test that MongoDB _id field is removed."""
    mock_review_collection.find_one = AsyncMock(return_value={"_id": "...", "order_id": 100})
    
    result = await review_dao.get_by_order_id(100)
    
    result_dict = result.model_dump()
    assert "_id" not in result_dict  # Single assertion

# Good - Multiple related assertions
@pytest.mark.asyncio
async def test_create_review_success(self, review_service):
    """Test successful review creation."""
    # ... setup ...
    
    review = await review_service.create_review(review_data)
    
    # Related assertions about the created review
    assert review.order_id == 100
    assert review.stars == 5
    assert review.content == "Excellent!"
```

### 4. Use Fixtures for Common Setup
Extract common setup code into fixtures:

```python
# Good - Reusable fixture
@pytest.fixture
def sample_review_data():
    return {
        "order_id": 100,
        "customer_id": 1,
        "provider_id": 2,
        "stars": 5,
        "content": "Great!"
    }

@pytest.mark.asyncio
async def test_create(self, review_dao, sample_review_data):
    result = await review_dao.create(Review(**sample_review_data))
    assert result.order_id == sample_review_data["order_id"]

# Bad - Duplicate setup in each test
@pytest.mark.asyncio
async def test_create_1(self, review_dao):
    data = {"order_id": 100, "customer_id": 1, ...}  # Duplicated
    result = await review_dao.create(Review(**data))
    assert result.order_id == 100

@pytest.mark.asyncio
async def test_create_2(self, review_dao):
    data = {"order_id": 100, "customer_id": 1, ...}  # Duplicated
    result = await review_dao.create(Review(**data))
    assert result.stars == 5
```

### 5. Test Edge Cases
Always test boundary conditions and edge cases:

```python
# Test with minimum value
@pytest.mark.asyncio
async def test_create_review_with_min_stars(self, review_dao):
    review = Review(order_id=100, customer_id=1, provider_id=2, stars=1)  # Minimum
    ...

# Test with maximum value
@pytest.mark.asyncio
async def test_create_review_with_max_stars(self, review_dao):
    review = Review(order_id=100, customer_id=1, provider_id=2, stars=5)  # Maximum
    ...

# Test with optional field missing
@pytest.mark.asyncio
async def test_create_review_without_content(self, review_dao):
    review = Review(order_id=100, customer_id=1, provider_id=2, stars=5, content=None)
    ...

# Test with empty result
@pytest.mark.asyncio
async def test_get_reviews_for_provider_empty(self, review_dao):
    mock_collection.find = Mock(return_value=AsyncMock(to_list=AsyncMock(return_value=[])))
    ...
```

### 6. Keep Tests Simple
Tests should be easy to read and understand:

```python
# Good - Simple and clear
@pytest.mark.asyncio
async def test_get_rating_success(self, rating_dao, mock_rating_collection):
    mock_rating_collection.find_one = AsyncMock(
        return_value={"provider_id": 2, "average_rating": 4.5, "total_reviews": 10}
    )
    
    rating = await rating_dao.get_by_provider_id(2)
    
    assert rating.provider_id == 2
    assert rating.average_rating == 4.5

# Bad - Overly complex
@pytest.mark.asyncio
async def test_rating_operations(self, rating_dao, mock_rating_collection):
    # Tests too many things at once
    for provider_id in range(1, 10):
        for avg in [1.0, 2.5, 3.7, 4.5, 5.0]:
            mock_rating_collection.find_one = AsyncMock(...)
            rating = await rating_dao.get_by_provider_id(provider_id)
            # Complex assertions...
```

### 7. Use Descriptive Assertion Messages
Add messages to make failures easier to understand:

```python
# Good - Clear failure message
assert result.average_rating == 4.0, \
    f"Expected average rating 4.0 but got {result.average_rating}. " \
    f"Calculation should be (5+4+3)/3=4.0"

# Good - Descriptive variable names make message unnecessary
expected_average_rating = 4.0
actual_average_rating = result.average_rating
assert actual_average_rating == expected_average_rating
```

## Troubleshooting

### Common Issues

#### 1. Tests Not Discovered
**Symptom**: `pytest` doesn't find any tests

**Solution**:
```bash
# Check test discovery
poetry run pytest --collect-only

# Verify file naming
# - Test files: test_*.py
# - Test classes: Test*
# - Test functions: test_*

# Check pytest.ini configuration
cat pytest.ini
```

#### 2. Import Errors
**Symptom**: `ModuleNotFoundError: No module named 'review_service'`

**Solution**:
```bash
# Install dependencies
poetry install

# Verify installation
poetry run python -c "import review_service; print(review_service.__file__)"

# Check pytest.ini pythonpath
# pytest.ini should have: pythonpath = src
```

#### 3. Async Test Failures
**Symptom**: `TypeError: object MagicMock can't be used in 'await' expression`

**Solution**:
```python
# Use AsyncMock instead of MagicMock
from unittest.mock import AsyncMock

# Bad
mock_collection.find_one = MagicMock(return_value={...})

# Good
mock_collection.find_one = AsyncMock(return_value={...})
```

#### 4. Fixture Not Found
**Symptom**: `fixture 'mock_event_publisher' not found`

**Solution**:
```bash
# Check conftest.py is in correct location
ls src/review_service/tests/unit/conftest.py

# Verify fixture is defined
grep "def mock_event_publisher" src/review_service/tests/unit/conftest.py

# Check fixture scope
# Fixtures should be function-scoped (default) for test independence
```

#### 5. Coverage Not 100%
**Symptom**: Coverage report shows missing lines

**Solution**:
```bash
# Generate HTML report to see uncovered lines
poetry run pytest --cov=review_service --cov-report=html
open htmlcov/index.html

# Check which lines are missing
poetry run pytest --cov=review_service --cov-report=term-missing

# Write tests for uncovered lines
```

#### 6. Mock Not Being Called
**Symptom**: `AssertionError: Expected 'mock_method' to have been called once`

**Solution**:
```python
# Verify mock is set up correctly
review_service.review_dao.create = AsyncMock(return_value=...)

# Check method signature matches
# Make sure you're mocking the right method with correct arguments

# Use assert_called_once() or assert_called_once_with(args)
review_service.review_dao.create.assert_called_once()

# Debug by printing call history
print(review_service.review_dao.create.call_args_list)
```

#### 7. Datetime Comparison Issues
**Symptom**: Datetime assertions fail due to microsecond differences

**Solution**:
```python
from datetime import datetime, timedelta

# Don't compare exact datetimes
# Bad
assert result.created_at == datetime.now()

# Good - Use timedelta for fuzzy comparison
now = datetime.now()
assert abs((result.created_at - now).total_seconds()) < 1

# Or freeze time with pytest-freezegun
from freezegun import freeze_time

@freeze_time("2024-01-15 10:00:00")
@pytest.mark.asyncio
async def test_with_frozen_time(self):
    # Now datetime.now() is always "2024-01-15 10:00:00"
    ...
```

### Debug Strategies

**1. Print Debugging**
```python
@pytest.mark.asyncio
async def test_debug(self, review_service):
    result = await review_service.create_review(data)
    print(f"Result: {result}")  # Use -s flag to see output
    print(f"Mock calls: {review_service.review_dao.create.call_args_list}")
```

**2. Use pytest --pdb**
```bash
# Drop into debugger on failure
poetry run pytest src/review_service/tests/unit/ --pdb

# Commands in debugger:
# p variable    - Print variable
# l             - List source code
# n             - Next line
# c             - Continue
# q             - Quit
```

**3. Check Mock Call History**
```python
# See all calls
print(mock_object.call_args_list)

# See if called
print(mock_object.called)

# See call count
print(mock_object.call_count)

# See last call
print(mock_object.call_args)
```

**4. Verify Fixture Setup**
```python
@pytest.mark.asyncio
async def test_debug_fixture(self, review_service, mock_event_publisher):
    print(f"ReviewService: {review_service}")
    print(f"ReviewDAO: {review_service.review_dao}")
    print(f"EventPublisher mock: {mock_event_publisher}")
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/review-service-tests.yml`:

```yaml
name: Review Service Tests

on:
  push:
    branches: [main, develop]
    paths:
      - 'services/review-service/**'
  pull_request:
    branches: [main, develop]
    paths:
      - 'services/review-service/**'

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12', '3.13']
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      
      - name: Install dependencies
        working-directory: ./services/review-service
        run: |
          poetry install --no-interaction --no-ansi
      
      - name: Run tests with coverage
        working-directory: ./services/review-service
        run: |
          poetry run pytest src/review_service/tests/unit/ -v \
            --cov=review_service.services \
            --cov=review_service.dao \
            --cov=review_service.core.config \
            --cov-report=xml \
            --cov-report=term-missing
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./services/review-service/coverage.xml
          flags: review-service
          name: review-service-coverage
      
      - name: Check coverage threshold
        working-directory: ./services/review-service
        run: |
          poetry run pytest src/review_service/tests/unit/ \
            --cov=review_service.services \
            --cov=review_service.dao \
            --cov=review_service.core.config \
            --cov-fail-under=100
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/sh
# Review Service pre-commit hook

echo "Running Review Service tests..."

cd services/review-service

# Run tests
poetry run pytest src/review_service/tests/unit/ -q --cov=review_service --cov-fail-under=100

# Check exit code
if [ $? -ne 0 ]; then
  echo "Tests failed. Commit aborted."
  exit 1
fi

echo "All tests passed!"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### GitLab CI Example

Create `.gitlab-ci.yml`:

```yaml
review-service-tests:
  stage: test
  image: python:3.13
  
  before_script:
    - cd services/review-service
    - pip install poetry
    - poetry install --no-interaction
  
  script:
    - poetry run pytest src/review_service/tests/unit/ -v
        --cov=review_service.services
        --cov=review_service.dao
        --cov=review_service.core.config
        --cov-report=xml
        --cov-report=term-missing
  
  coverage: '/TOTAL.*\s+(\d+%)$/'
  
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  
  only:
    changes:
      - services/review-service/**/*
```

## Maintenance and Updates

### Adding New Tests

When adding new functionality:

1. **Write test first** (TDD approach)
```python
@pytest.mark.asyncio
async def test_new_feature(self, review_service):
    """Test new feature description."""
    # This test will fail initially
    result = await review_service.new_feature()
    assert result is not None
```

2. **Implement feature**
3. **Run tests to verify**
4. **Refactor if needed**
5. **Verify 100% coverage maintained**

### Updating Existing Tests

When modifying code:

1. **Update affected tests**
2. **Run full test suite**
3. **Check coverage hasn't decreased**
4. **Update documentation if needed**

### Review Checklist

Before merging code:

- [ ] All tests pass
- [ ] Coverage is 100% for core modules
- [ ] New tests follow AAA pattern
- [ ] Async methods use AsyncMock
- [ ] MongoDB _id removal verified
- [ ] Event publishing verified (if applicable)
- [ ] Test names are descriptive
- [ ] No print statements in tests (use logging if needed)
- [ ] Documentation updated

## Resources

### Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### Related Files
- `TEST_SUMMARY.md` - Test results and summary
- `UNIT_TEST_QUICK_START.md` - Quick reference guide
- `conftest.py` - Fixture definitions
- `pytest.ini` - Pytest configuration

### Internal Resources
- User Service Tests - Similar patterns, 92 tests, 96% coverage
- Notification Service Tests - Template for 100% coverage, 38 tests
- Auth Service Tests - 33 tests, ~80% coverage

## Conclusion

This test suite provides comprehensive coverage of the Review Service with:

- ✅ **39 tests** covering all critical functionality
- ✅ **100% coverage** of core business logic
- ✅ **0.14s execution** - fast feedback loop
- ✅ **Well-organized** - clear structure and patterns
- ✅ **Maintainable** - consistent style and documentation
- ✅ **CI-ready** - easy integration with CI/CD pipelines

The test suite serves as both quality assurance and living documentation for the Review Service.

---

**Last Updated**: October 24, 2025  
**Review Service Version**: 1.0.0  
**Test Framework**: pytest 7.4.4  
**Python Version**: 3.13.3
