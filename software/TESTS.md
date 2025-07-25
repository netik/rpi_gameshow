# Testing Guide for Dirty Talk Game Show

This document provides comprehensive information about testing the game show application, including setup, execution, and best practices.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Writing Tests](#writing-tests)
- [Test Fixtures](#test-fixtures)
- [Coverage and Quality](#coverage-and-quality)
- [Troubleshooting](#troubleshooting)
- [CI/CD Integration](#cicd-integration)

## Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install -e ".[test]"

# Verify installation
python -c "import pytest; print('Pytest installed successfully')"
```

### Basic Test Execution

```bash
# Run all unit tests
python tests/run_tests.py --type unit

# Run all tests with coverage
python tests/run_tests.py --type all --coverage

# Run specific test file
pytest tests/unit/test_context.py
```

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and common fixtures
├── run_tests.py             # Test runner script (executable)
├── README.md               # Detailed testing documentation
├── unit/                   # Unit tests for individual components
│   ├── test_gamestate.py   # GameState enum tests
│   ├── test_context.py     # Context class tests
│   └── test_particle.py    # Particle system tests
├── integration/            # Integration tests for component interactions
│   └── test_game_flow.py   # Game flow and state transition tests
├── gui/                    # GUI tests (requires display)
│   └── test_display.py     # Display and rendering tests
└── hardware/               # Hardware-specific tests
    └── (future tests)
```

## Running Tests

### Using the Test Runner Script

The `tests/run_tests.py` script provides a convenient way to run different types of tests:

```bash
# Basic usage
python tests/run_tests.py --type unit

# With coverage reporting
python tests/run_tests.py --type all --coverage

# Verbose output
python tests/run_tests.py --type integration --verbose

# Parallel execution
python tests/run_tests.py --type all --parallel 4

# Available options
python tests/run_tests.py --help
```

### Direct Pytest Usage

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m gui

# Run specific test file
pytest tests/unit/test_context.py

# Run specific test function
pytest tests/unit/test_context.py::TestContext::test_context_initialization

# Run with coverage
pytest --cov=. --cov-report=html

# Run with verbose output
pytest -v

# Run with debug output
pytest -v -s --tb=long
```

### Test Markers

Tests are categorized using pytest markers:

```bash
# Run unit tests only
pytest -m unit

# Run integration tests only
pytest -m integration

# Run GUI tests only
pytest -m gui

# Run hardware tests only
pytest -m hardware

# Run slow tests
pytest -m slow

# Skip GUI tests (useful for CI)
pytest -m "not gui"
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation

**Characteristics**:
- Fast execution (< 1 second per test)
- Mocked external dependencies
- Focus on single class/function behavior
- High coverage requirements

**Examples**:
- `test_gamestate.py`: GameState enum functionality
- `test_context.py`: Context class state management
- `test_particle.py`: Particle system behavior

**Running**:
```bash
python tests/run_tests.py --type unit
# or
pytest tests/unit/
```

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test component interactions and workflows

**Characteristics**:
- Medium execution time (1-5 seconds per test)
- Some real dependencies, some mocked
- Test complete workflows
- Verify component cooperation

**Examples**:
- `test_game_flow.py`: Complete game initialization and state transitions
- Data persistence workflows
- Component interaction patterns

**Running**:
```bash
python tests/run_tests.py --type integration
# or
pytest tests/integration/
```

### 3. GUI Tests (`tests/gui/`)

**Purpose**: Test user interface and display functionality

**Characteristics**:
- Slower execution (requires display)
- Real pygame display
- Visual verification
- May require actual screen

**Examples**:
- `test_display.py`: Screen rendering, text display, modal dialogs
- UI component rendering
- User interaction simulation

**Running**:
```bash
python tests/run_tests.py --type gui
# or
pytest tests/gui/
```

### 4. Hardware Tests (`tests/hardware/`)

**Purpose**: Test hardware-specific functionality

**Characteristics**:
- Variable execution time
- May require actual hardware
- GPIO and serial communication
- Hardware simulation support

**Examples**:
- Button input testing
- LED output verification
- Serial communication
- GPIO pin management

**Running**:
```bash
python tests/run_tests.py --type hardware
# or
pytest tests/hardware/
```

## Writing Tests

### Unit Test Example

```python
"""Example unit test for a new component."""

import pytest
from unittest.mock import Mock, patch
from your_module import YourClass


class TestYourClass:
    """Test cases for YourClass."""
    
    def test_initialization(self):
        """Test YourClass initialization with default values."""
        with patch('dependency.module') as mock_dep:
            instance = YourClass()
            assert instance.some_property == expected_value
            mock_dep.assert_called_once()
    
    def test_method_behavior(self):
        """Test specific method behavior."""
        with patch('dependency.module') as mock_dep:
            instance = YourClass()
            result = instance.some_method("input")
            assert result == "expected_output"
    
    def test_error_handling(self):
        """Test error conditions."""
        with patch('dependency.module', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                YourClass()
```

### Integration Test Example

```python
"""Example integration test."""

import pytest
from unittest.mock import Mock, patch
from Context import Context
from GameState import GameState


class TestGameIntegration:
    """Integration tests for game components."""
    
    def test_component_interaction(self):
        """Test interaction between multiple components."""
        with patch('pygame.time.Clock'), \
             patch('Sound.Sound'), \
             patch('pygame.sprite.Group'):
            
            context = Context()
            
            # Test component interaction
            context.state = GameState.RUNNING
            context.player_buzzed_in = 1
            
            # Verify state consistency
            assert context.state == GameState.RUNNING
            assert context.player_buzzed_in == 1
```

### GUI Test Example

```python
"""Example GUI test."""

import pytest
import pygame


@pytest.mark.gui
class TestDisplay:
    """Test cases for display functionality."""
    
    def test_screen_initialization(self):
        """Test screen initialization."""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        
        assert screen.get_size() == (800, 600)
        
        pygame.quit()
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

### Available Fixtures

```python
@pytest.fixture
def temp_state_file():
    """Create a temporary state file for testing."""
    # Returns temporary file path, cleans up automatically

@pytest.fixture
def mock_serial_port():
    """Mock serial port for testing."""
    # Returns mock serial port object

@pytest.fixture
def mock_gpio():
    """Mock GPIO for testing."""
    # Returns mock GPIO object

@pytest.fixture
def sample_game_state():
    """Sample game state data for testing."""
    # Returns sample game state dictionary

@pytest.fixture
def mock_screen():
    """Mock pygame screen for testing."""
    # Returns mock screen object

@pytest.fixture
def mock_font():
    """Mock pygame font for testing."""
    # Returns mock font object
```

### Using Fixtures

```python
def test_with_fixtures(temp_state_file, mock_serial_port):
    """Test using multiple fixtures."""
    # temp_state_file is a temporary file path
    # mock_serial_port is a mock serial port object
    
    # Your test code here
    pass
```

## Coverage and Quality

### Coverage Goals

- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 80%+ line coverage
- **Overall**: 85%+ line coverage

### Running Coverage

```bash
# Generate coverage report
python tests/run_tests.py --type all --coverage

# View HTML coverage report
open htmlcov/index.html

# Generate coverage report in terminal
pytest --cov=. --cov-report=term-missing
```

### Quality Checks

```bash
# Run type checking
mypy .

# Run linting
flake8 .

# Run all quality checks
python tests/run_tests.py --type all --coverage && mypy . && flake8 .
```

## Troubleshooting

### Common Issues

#### 1. Pygame Import Errors
```bash
# Error: Unable to import pygame
# Solution: Install pygame and configure SDL drivers
pip install pygame
export SDL_VIDEODRIVER=dummy  # For headless testing
```

#### 2. Mock Assertion Errors
```bash
# Error: Mock not called as expected
# Solution: Check mock configuration and call expectations
# Use mock.assert_called_with() for specific arguments
```

#### 3. File Permission Errors
```bash
# Error: Permission denied when creating test files
# Solution: Ensure test directories are writable
chmod 755 tests/
```

#### 4. Hardware Dependency Errors
```bash
# Error: Hardware not available for testing
# Solution: Use appropriate mocks for hardware tests
pytest -m "not hardware"
```

### Debug Mode

```bash
# Run tests with maximum debug output
pytest -v -s --tb=long --maxfail=1

# Run specific test with debug
pytest tests/unit/test_context.py::TestContext::test_context_initialization -v -s
```

### Test Isolation

```bash
# Run tests in isolation
pytest --dist=no

# Run tests sequentially
pytest -n0
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -e ".[test]"
    
    - name: Run tests
      run: |
        python tests/run_tests.py --type all --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### GitLab CI Example

```yaml
test:
  image: python:3.12
  script:
    - pip install -e ".[test]"
    - python tests/run_tests.py --type all --coverage
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### Local Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run tests before commit
python tests/run_tests.py --type unit
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## Best Practices

### 1. Test Organization
- Use descriptive test class and method names
- Group related tests in the same class
- Use docstrings to explain test purpose
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Mocking Strategy
- Mock external dependencies (pygame, hardware, filesystem)
- Use `unittest.mock.patch` for dependency injection
- Mock at the appropriate level (module vs. class vs. method)
- Verify mock calls when important

### 3. Assertions
- Use specific assertions (assertEqual, assertIn, etc.)
- Test both positive and negative cases
- Verify side effects and state changes
- Use custom assertion messages for clarity

### 4. Test Data
- Use fixtures for common test data
- Create realistic but minimal test scenarios
- Avoid hardcoded values when possible
- Use factories for complex object creation

### 5. Error Handling
- Test error conditions and edge cases
- Verify proper exception handling
- Test boundary conditions
- Use pytest.raises for exception testing

## Future Enhancements

1. **Performance Tests**: Add benchmarks for critical paths
2. **Stress Tests**: Test system behavior under load
3. **Memory Tests**: Verify no memory leaks
4. **Accessibility Tests**: Ensure UI is accessible
5. **Localization Tests**: Test multi-language support
6. **Security Tests**: Verify input validation and security
7. **Compatibility Tests**: Test across different Python versions

## Contributing to Tests

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this documentation if needed
5. Add appropriate test markers and categories
6. Follow the established patterns and conventions 