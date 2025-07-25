# Testing Guide for Game Show Application

This directory contains comprehensive tests for the game show application. The testing strategy is designed to ensure reliability, maintainability, and proper functionality across different environments.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and common fixtures
├── run_tests.py             # Test runner script
├── README.md               # This file
├── unit/                   # Unit tests for individual components
│   ├── test_gamestate.py   # GameState enum tests
│   ├── test_context.py     # Context class tests
│   └── test_particle.py    # Particle system tests
├── integration/            # Integration tests for component interactions
│   └── test_game_flow.py   # Game flow and state transition tests
├── gui/                    # GUI tests (requires display)
│   └── (future tests)
└── hardware/               # Hardware-specific tests
    └── (future tests)
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single classes, functions, or modules
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution
- **Examples**: GameState enum, Context class, Particle classes

### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and workflows
- **Scope**: Multiple components working together
- **Dependencies**: Some mocked, some real
- **Speed**: Medium execution time
- **Examples**: Game flow, state transitions, data persistence

### 3. GUI Tests (`tests/gui/`)
- **Purpose**: Test user interface components
- **Scope**: Display rendering, user interactions
- **Dependencies**: Pygame display, may require actual screen
- **Speed**: Slower execution
- **Examples**: Screen rendering, button interactions, modal dialogs

### 4. Hardware Tests (`tests/hardware/`)
- **Purpose**: Test hardware-specific functionality
- **Scope**: GPIO, serial communication, LED control
- **Dependencies**: Actual hardware or hardware simulators
- **Speed**: Variable execution time
- **Examples**: Button input, LED output, serial communication

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -e ".[test]"
```

2. Ensure pygame is properly configured for testing (handled by conftest.py)

### Basic Test Execution

```bash
# Run all unit tests
python tests/run_tests.py --type unit

# Run all integration tests
python tests/run_tests.py --type integration

# Run all tests
python tests/run_tests.py --type all

# Run with coverage report
python tests/run_tests.py --type all --coverage

# Run with verbose output
python tests/run_tests.py --type unit --verbose

# Run tests in parallel
python tests/run_tests.py --type all --parallel 4
```

### Direct Pytest Usage

```bash
# Run specific test file
pytest tests/unit/test_context.py

# Run specific test function
pytest tests/unit/test_context.py::TestContext::test_context_initialization

# Run tests with specific marker
pytest -m unit

# Run tests with coverage
pytest --cov=. --cov-report=html
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `setup_pygame`: Initialize pygame for testing
- `temp_state_file`: Temporary file for state persistence tests
- `mock_serial_port`: Mock serial port for hardware tests
- `mock_gpio`: Mock GPIO for Raspberry Pi tests
- `sample_game_state`: Sample game state data
- `mock_screen`: Mock pygame screen
- `mock_font`: Mock pygame font

## Writing New Tests

### Unit Test Example

```python
"""Unit test example for a new component."""

import pytest
from unittest.mock import Mock, patch
from your_module import YourClass


class TestYourClass:
    """Test cases for YourClass."""
    
    def test_initialization(self):
        """Test YourClass initialization."""
        with patch('dependency.module') as mock_dep:
            instance = YourClass()
            assert instance.some_property == expected_value
    
    def test_method_behavior(self):
        """Test specific method behavior."""
        with patch('dependency.module') as mock_dep:
            instance = YourClass()
            result = instance.some_method("input")
            assert result == "expected_output"
```

### Integration Test Example

```python
"""Integration test example."""

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
            # ...
```

## Test Best Practices

### 1. Test Organization
- Use descriptive test class and method names
- Group related tests in the same class
- Use docstrings to explain test purpose

### 2. Mocking Strategy
- Mock external dependencies (pygame, hardware, filesystem)
- Use `unittest.mock.patch` for dependency injection
- Mock at the appropriate level (module vs. class vs. method)

### 3. Assertions
- Use specific assertions (assertEqual, assertIn, etc.)
- Test both positive and negative cases
- Verify side effects and state changes

### 4. Test Data
- Use fixtures for common test data
- Create realistic but minimal test scenarios
- Avoid hardcoded values when possible

### 5. Error Handling
- Test error conditions and edge cases
- Verify proper exception handling
- Test boundary conditions

## Coverage Goals

- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 80%+ line coverage
- **Overall**: 85%+ line coverage

## Continuous Integration

Tests should be run automatically in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pip install -e ".[test]"
    python tests/run_tests.py --type all --coverage
```

## Troubleshooting

### Common Issues

1. **Pygame Import Errors**: Ensure pygame is installed and SDL drivers are configured
2. **Mock Assertion Errors**: Check that mocks are properly configured
3. **File Permission Errors**: Ensure test directories are writable
4. **Hardware Dependency Errors**: Use appropriate mocks for hardware tests

### Debug Mode

Run tests with debug output:

```bash
pytest -v -s --tb=long
```

## Future Enhancements

1. **Performance Tests**: Add benchmarks for critical paths
2. **Stress Tests**: Test system behavior under load
3. **Memory Tests**: Verify no memory leaks
4. **Accessibility Tests**: Ensure UI is accessible
5. **Localization Tests**: Test multi-language support

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this documentation if needed
5. Add appropriate test markers and categories 