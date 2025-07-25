# Dirty Talk Game Show

A four-player, timed and buzzer-based game show software compatible with a variety of custom hardware, including Raspberry Pi GPIO and serial connections.

## Overview

This project implements a complete game show buzzer system for "The Dirty Talk Game Show" with the following features:

- **Four-player buzzer system** with individual LED indicators
- **Real-time countdown timer** with configurable duration
- **Score tracking** for each player
- **Customizable player names** and themes
- **Multiple platform support**: Raspberry Pi (GPIO), PC (development), and PC with serial hardware
- **Sound effects** and visual feedback
- **State persistence** across game sessions

## Hardware Support

- **Raspberry Pi**: Direct GPIO control for buttons and LEDs
- **PC Development**: Keyboard simulation of buzzers
- **Serial Hardware**: Support for external buzzer boards via serial connection

## Installation

### Prerequisites

- Python 3.12 or higher
- Pygame 2.6.1 or higher
- PySerial 3.5 or higher (for serial hardware support)

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd rpi_gameshow/software

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Install test dependencies (optional)
pip install -e ".[test]"
```

### Development Setup

```bash
# Install with development dependencies
pip install -e ".[test]"

# Run tests to verify installation
python tests/run_tests.py --type unit
```

## Usage

### Basic Game Operation

```bash
# Run the game
python gameshow.py
```

### Controls

- **Space**: Start/Stop timer
- **1-4**: Add points to players 1-4
- **Q, W, E, R**: Subtract points from players 1-4
- **P**: Add 5 seconds to timer
- **L**: Subtract 5 seconds from timer
- **N**: Edit player names
- **H or ?**: Show help
- **ESC**: Quit game

### Configuration

Edit `config.py` to customize:
- Number of players
- Timer duration
- Display settings
- Hardware platform
- Theme colors
- Sound settings

## Testing

The project includes a comprehensive testing suite with unit, integration, and GUI tests.

### Quick Test Commands

```bash
# Run all unit tests
python tests/run_tests.py --type unit

# Run all integration tests
python tests/run_tests.py --type integration

# Run all tests with coverage
python tests/run_tests.py --type all --coverage

# Run tests in parallel
python tests/run_tests.py --type all --parallel 4
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **GUI Tests**: Display and rendering tests
- **Hardware Tests**: GPIO and serial communication tests

For detailed testing information, see [TESTS.md](TESTS.md) or [tests/README.md](tests/README.md).

## Project Structure

```
software/
├── gameshow.py          # Main game application
├── Context.py           # Game state management
├── GameState.py         # Game state enumeration
├── config.py            # Configuration settings
├── Sound.py             # Sound management
├── Particle.py          # Visual effects system
├── NameEditor.py        # Player name editing
├── drawutil.py          # Drawing utilities
├── particleutil.py      # Particle system utilities
├── helpinfo.py          # Help text and controls
├── pygame_textinput.py  # Text input handling
├── ptext.py             # Text rendering library
├── tests/               # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   ├── gui/             # GUI tests
│   └── hardware/        # Hardware tests
├── fonts/               # Font files
├── sounds/              # Sound effect files
└── images/              # Image assets
```

## Development

### Code Style

The project follows modern Python practices:
- Type hints throughout
- Comprehensive docstrings
- PEP 8 compliance
- MyPy type checking

### Adding Features

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update documentation

### Running Type Checks

```bash
# Run MyPy type checking
mypy .

# Run with strict mode
mypy --strict .
```

## Platform Support

### Raspberry Pi (Production)
- Direct GPIO control
- Hardware buzzer support
- LED indicator control
- Full-screen display

### PC Development
- Keyboard simulation
- Windowed display
- Debug LED visualization
- Sound effect testing

### Serial Hardware
- External buzzer board support
- Serial communication
- Hardware abstraction layer

## Troubleshooting

### Common Issues

1. **Pygame Display Errors**: Ensure SDL drivers are properly configured
2. **Sound Issues**: Check audio device configuration
3. **GPIO Errors**: Verify Raspberry Pi GPIO permissions
4. **Serial Connection**: Check device permissions and port configuration

### Debug Mode

Run with debug output:
```bash
python gameshow.py --debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

[Add your license information here]

## Acknowledgments

- Pygame community for the excellent game development library
- Raspberry Pi Foundation for the GPIO interface
- Contributors to the original game show concept
