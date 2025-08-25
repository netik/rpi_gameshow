"""
Unit tests for hardware.py module.
"""

import pytest
from unittest.mock import Mock, patch
from hardware import (
    serial_send, button_event, set_led, set_all_leds, 
    setup_serial, setup_gpio
)
from Context import Context


class TestHardware:
    """Test cases for hardware module."""
    
    @pytest.fixture
    def mock_context(self):
        """Create a mock context for testing."""
        context = Mock(spec=Context)
        context.serial_port = Mock()
        context.led_state = [False, False, False, False]
        context.player_buzzed_in = -1
        return context
    
    @pytest.fixture
    def mock_serial_port(self):
        """Create a mock serial port."""
        mock_port = Mock()
        mock_port.write.return_value = None
        mock_port.flush.return_value = None
        mock_port.readline.return_value = b"OK\n"
        mock_port.isOpen.return_value = True
        mock_port.inWaiting.return_value = 0
        mock_port.reset_input_buffer.return_value = None
        mock_port.reset_output_buffer.return_value = None
        return mock_port
    
    @patch('hardware.config.PLATFORM', 'pcserial')
    def test_serial_send_success(self, mock_context, mock_serial_port):
        """Test successful serial send."""
        mock_context.serial_port = mock_serial_port
        
        result = serial_send(mock_context, b"TEST")
        
        assert result is True
        mock_context.serial_port.write.assert_called_once_with(b"TEST")
        mock_context.serial_port.flush.assert_called_once()
        mock_context.serial_port.readline.assert_called_once()
    
    @patch('hardware.config.PLATFORM', 'pc')
    def test_serial_send_wrong_platform(self, mock_context):
        """Test serial send with wrong platform."""
        result = serial_send(mock_context, b"TEST")
        assert result is False
    
    @patch('hardware.config.PLATFORM', 'pcserial')
    def test_button_event_serial_mode(self, mock_context):
        """Test button event in serial mode."""
        button_event(mock_context, 2)
        assert mock_context.player_buzzed_in == 1  # channel - 1
    
    @patch('hardware.config.PLATFORM', 'rpi')
    @patch('hardware.config.PLAYER_REVERSE_MAP', {16: 0, 17: 1, 18: 2, 19: 3})
    def test_button_event_gpio_mode(self, mock_context):
        """Test button event in GPIO mode."""
        button_event(mock_context, 17)
        assert mock_context.player_buzzed_in == 1
    
    @patch('hardware.config.PLATFORM', 'rpi')
    def test_set_led_rpi_mode(self, mock_context):
        """Test setting LED in RPi mode."""
        mock_context.led_state = [False, False, False, False]
        
        with patch('hardware.config.GPIO_LED_MAP', [20, 21, 22, 23]):
            # Mock the GPIO module to avoid import errors
            with patch('hardware.GPIO', create=True) as mock_gpio:
                set_led(mock_context, 1, True)
                mock_gpio.output.assert_called_once_with(21, True)
        
        assert mock_context.led_state[1] is True
    
    @patch('hardware.config.PLATFORM', 'pcserial')
    def test_set_led_serial_mode(self, mock_context, mock_serial_port):
        """Test setting LED in serial mode."""
        mock_context.serial_port = mock_serial_port
        mock_context.led_state = [False, False, False, False]
        
        set_led(mock_context, 2, True)
        
        assert mock_context.led_state[2] is True
        mock_context.serial_port.write.assert_called_once_with(b"LED 3 1\n")
    
    @patch('hardware.config.PLATFORM', 'pcserial')
    def test_set_led_exclusive(self, mock_context, mock_serial_port):
        """Test setting LED with exclusive mode."""
        mock_context.serial_port = mock_serial_port
        mock_context.led_state = [True, True, True, True]
        
        with patch('hardware.set_all_leds') as mock_set_all:
            set_led(mock_context, 1, True, exclusive=True)
            
            mock_set_all.assert_called_once_with(mock_context, False)
            assert mock_context.led_state[1] is True
    
    @patch('hardware.config.PLATFORM', 'pcserial')
    def test_set_all_leds(self, mock_context, mock_serial_port):
        """Test setting all LEDs."""
        mock_context.serial_port = mock_serial_port
        mock_context.led_state = [False, False, False, False]
        
        with patch('hardware.set_led') as mock_set_led:
            set_all_leds(mock_context, True)
            
            # Should call set_led for each player
            assert mock_set_led.call_count == 4
            # Check that it was called with correct parameters
            mock_set_led.assert_any_call(mock_context, 0, True, False)
            mock_set_led.assert_any_call(mock_context, 1, True, False)
            mock_set_led.assert_any_call(mock_context, 2, True, False)
            mock_set_led.assert_any_call(mock_context, 3, True, False)
    
    @patch('hardware.config.PLATFORM', 'pcserial')
    @patch('hardware.config.SERIAL_DEVICE', '/dev/test')
    @patch('hardware.os.path.exists')
    def test_setup_serial_success(self, mock_exists, mock_context):
        """Test successful serial setup."""
        mock_exists.return_value = True
        
        with patch('hardware.serial.Serial') as mock_serial_class:
            mock_serial_instance = Mock()
            mock_serial_instance.isOpen.return_value = True
            mock_serial_instance.readline.side_effect = [b"WAIT\r\n", b"RESET OK\r\n"]
            mock_serial_class.return_value = mock_serial_instance
            
            result = setup_serial(mock_context, '/dev/test')
            
            assert result == mock_serial_instance
            assert mock_context.serial_port == mock_serial_instance
            mock_serial_instance.reset_input_buffer.assert_called_once()
            mock_serial_instance.reset_output_buffer.assert_called_once()
    
    @patch('hardware.config.PLATFORM', 'pcserial')
    @patch('hardware.config.SERIAL_DEVICE', '/dev/test')
    @patch('hardware.os.path.exists')
    def test_setup_serial_device_not_found(self, mock_exists, mock_context):
        """Test serial setup with device not found."""
        mock_exists.return_value = False
        
        with patch('hardware.config') as mock_config:
            result = setup_serial(mock_context, '/dev/test')
            
            assert result is False
            mock_config.PLATFORM = 'pc'  # Should fall back to PC mode
    
    @patch('hardware.config.PLATFORM', 'pc')
    def test_setup_serial_wrong_platform(self, mock_context):
        """Test serial setup with wrong platform."""
        result = setup_serial(mock_context, '/dev/test')
        assert result is False
    
    @patch('hardware.config.PLATFORM', 'rpi')
    @patch('hardware.config.PLAYER_MAP', [16, 17, 18, 19])
    @patch('hardware.config.GPIO_LED_MAP', [20, 21, 22, 23])
    def test_setup_gpio_rpi_mode(self, mock_context):
        """Test GPIO setup in RPi mode."""
        # Mock the GPIO module to avoid import errors
        with patch('hardware.GPIO', create=True) as mock_gpio:
            setup_gpio(mock_context)
            
            # Check GPIO mode setup
            mock_gpio.setmode.assert_called_once_with(mock_gpio.BCM)
            
            # Check button setup
            assert mock_gpio.setup.call_count == 8  # 4 buttons + 4 LEDs
            mock_gpio.setup.assert_any_call(16, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP)
            mock_gpio.setup.assert_any_call(17, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP)
            mock_gpio.setup.assert_any_call(18, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP)
            mock_gpio.setup.assert_any_call(19, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP)
            
            # Check LED setup
            mock_gpio.setup.assert_any_call(20, mock_gpio.OUT)
            mock_gpio.setup.assert_any_call(21, mock_gpio.OUT)
            mock_gpio.setup.assert_any_call(22, mock_gpio.OUT)
            mock_gpio.setup.assert_any_call(23, mock_gpio.OUT)
            
            # Check event detection setup
            assert mock_gpio.add_event_detect.call_count == 4
            mock_gpio.add_event_detect.assert_any_call(16, mock_gpio.FALLING, button_event, bouncetime=50)
            
            # Check warnings disabled
            mock_gpio.setwarnings.assert_called_once_with(False)
    
    @patch('hardware.config.PLATFORM', 'pc')
    def test_setup_gpio_wrong_platform(self, mock_context):
        """Test GPIO setup with wrong platform."""
        setup_gpio(mock_context)
        # Should not call any GPIO functions since GPIO is not imported on PC platform
    
    @patch('hardware.config.PLATFORM', 'rpi')
    @patch('hardware.config.PLAYER_MAP', [16, 17, 18, 19])
    @patch('hardware.config.GPIO_LED_MAP', [20, 21, 22, 23])
    def test_setup_gpio_calls_set_all_leds(self, mock_context):
        """Test that GPIO setup calls set_all_leds."""
        with patch('hardware.set_all_leds') as mock_set_all, \
             patch('hardware.GPIO', create=True):
            setup_gpio(mock_context)
            # Should call set_all_leds
            mock_set_all.assert_called_once_with(mock_context)
