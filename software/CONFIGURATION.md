# Configuration Guide

This project now uses [Dynaconf](https://www.dynaconf.com/) for configuration management instead of hardcoded values in Python files.

## Configuration Files

### `settings.toml` (Main Configuration)
This is the primary configuration file containing all game settings, themes, and default values.

### `development.toml` (Development Overrides)
This file contains development-specific overrides that are loaded after the main settings.

### Environment Variables
You can also override settings using environment variables:
```bash
export PLATFORM=pc
export DEBUG_LEDS=true
```

## Key Benefits

1. **Environment-Specific Configuration**: Different settings for development, testing, and production
2. **Dynamic Configuration**: Change settings without restarting the application
3. **Type Safety**: Configuration values are properly typed
4. **Validation**: Dynaconf can validate configuration values
5. **Hot Reloading**: Configuration can be reloaded at runtime

## Configuration Structure

### Game Settings
- `PLAYERS`: Number of players (default: 4)
- `FPS`: Game loop frames per second (default: 60)
- `CLOCK_ENABLED`: Whether the game clock runs (default: true)
- `MAX_CLOCK`: Maximum clock time in milliseconds (default: 60000)

### Hardware Configuration
- `PLATFORM`: Platform type - "rpi", "pc", or "pcserial" (default: "pcserial")
- `PLAYER_MAP`: GPIO pin mappings for player buttons
- `GPIO_LED_MAP`: GPIO pin mappings for LED indicators

### Display Settings
- `DISPLAY_STYLE`: "windowed", "borderless", or "fullscreen" (default: "fullscreen")
- `DISPLAY_WINDOW_HEIGHT`: Display height (default: 1920)
- `DISPLAY_WINDOW_WIDTH`: Display width (default: 1080)

### Themes
Three built-in themes are available:
- `DT_THEME`: Dark theme with reds and pinks
- `BRIGHT_THEME`: Bright theme with blues and purples  
- `CLASSY_THEME`: Professional theme with blues and grays

## Usage in Code

### Basic Configuration Access
```python
import game_config as config

# Access configuration values
player_count = config.PLAYERS
platform = config.PLATFORM
theme_colors = config.THEME_COLORS
```

### Dynamic Configuration
```python
from game_config import settings, reload_config, switch_theme

# Get a specific setting
debug_mode = settings.get('DEBUG_LEDS', False)

# Set a setting
settings.set('PLATFORM', 'pc')

# Switch themes
switch_theme('BRIGHT_THEME')

# Reload configuration from files
reload_config()
```

## Environment-Specific Configuration

### Development
- Platform: PC
- Debug LEDs: Enabled
- Display: Windowed
- Background rendering: Enabled

### Production (Raspberry Pi)
- Platform: RPI
- Debug LEDs: Disabled
- Display: Fullscreen
- Background rendering: Disabled

## Adding New Configuration

1. Add the setting to `settings.toml`
2. Add a default value and type annotation in `game_config.py`
3. Update any code that needs to access the new setting

## Migration Notes

The old `config.py` has been renamed to `game_config.py` and all imports have been updated to use `import game_config as config` to maintain backward compatibility.

## Troubleshooting

### Configuration Not Loading
- Ensure `settings.toml` exists in the project root
- Check file permissions
- Verify TOML syntax

### Import Errors
- Ensure dynaconf is installed: `pip install dynaconf`
- Check that `game_config.py` exists and is properly formatted

### Theme Issues
- Verify theme names match exactly: `DT_THEME`, `BRIGHT_THEME`, `CLASSY_THEME`
- Check that color values are in the correct format (RGBA lists or hex strings)

