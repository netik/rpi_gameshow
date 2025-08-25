"""
hardware.py

Handles hardware interactions for the gameshow application, including GPIO and serial communication.
"""

import os
import serial
import game_config as config

DEBUG_SERIAL = False

# conditional importing of Raspberry PI if need be.
if config.PLATFORM == "rpi":
    from RPi.GPIO import GPIO

def serial_send(context, cmd):
    if config.PLATFORM == "pcserial":
        context.serial_port.write(cmd)
        context.serial_port.flush()
        print("sent: " + str(cmd)) if DEBUG_SERIAL else None
        resp = context.serial_port.readline()
        print("recv: " + str(resp)) if DEBUG_SERIAL else None
        return True
    return False


def button_event(context, channel):
    if context.serial_port and config.PLATFORM == "pcserial":
        context.player_buzzed_in = channel - 1
        return
    context.player_buzzed_in = config.PLAYER_REVERSE_MAP[channel]


def set_led(context, led, new_state, exclusive=False):
    if exclusive:
        set_all_leds(context, False)

    if config.PLATFORM == "rpi":
        GPIO.output(config.GPIO_LED_MAP[led], new_state)

    if config.PLATFORM == "pcserial":
        serial_send(context, b"LED %d %d\n" % ((led + 1), new_state))
    context.led_state[led] = new_state


def set_all_leds(context, new_state=False):
    for k in range(0, config.PLAYERS):
        set_led(context, k, new_state, False)


def setup_serial(context, device):
    """
    Configure and initialize serial communication for external hardware.

    This function sets up serial communication with external hardware (typically
    Arduino) that handles physical buttons and LEDs. It establishes the connection,
    waits for the hardware to reset, and verifies communication is working.

    Args:
        context (Context): Game context to store the serial port object
        device (str): Serial port device name (e.g., "/dev/cu.usbserial*")

    Returns:
        serial.Serial: Configured serial port object, or False if setup fails

    Note:
        - Only works when PLATFORM is set to "pcserial"
        - Falls back to PC mode if serial device doesn't exist
        - Waits for hardware reset and "RESET OK" message
        - Flushes input/output buffers after successful connection
        - Baud rate is fixed at 115200 with 8N1 configuration
    """
    if config.PLATFORM != "pcserial":
        return False

    # does the device exist?
    if not os.path.exists(config.SERIAL_DEVICE):
        print("Serial device %s does not exist." % config.SERIAL_DEVICE)
        print("Falling back to PC mode.")
        config.PLATFORM = "pc"
        return False

    context.serial_port = serial.Serial(
        device, 115200, bytesize=8, parity=serial.PARITY_NONE, stopbits=1, timeout=None
    )  # open serial port

    while not context.serial_port.isOpen():
        pass

    print("Serial port open")
    # sleep for board to reset as it resets on open
    print("Waiting for board to reset...")

    while True:
        line = context.serial_port.readline()
        print("recv: " + str(line)) if DEBUG_SERIAL else None
        if line == b"RESET OK\r\n":
            break

    print("Board reset")

    # flush the serial buffers at the start of the game
    if context.serial_port:
        context.serial_port.reset_input_buffer()
        context.serial_port.reset_output_buffer()

    return context.serial_port


def setup_gpio(context):
    """
    Setup Raspberry Pi GPIO pins for buttons and LEDs.

    This function configures the GPIO pins for player button inputs and LED outputs
    when running on Raspberry Pi hardware. It sets up button detection with
    debouncing and configures LED pins as outputs.

    Args:
        context (Context): Game context (not used in this function but required for consistency)

    Note:
        - Only runs when PLATFORM is set to "rpi"
        - Uses BCM pin numbering scheme
        - Button pins are configured as inputs with internal pull-up resistors
        - LED pins are configured as outputs
        - Button events are detected on falling edge (button press to ground)
        - Debounce time is set to 50ms to prevent false triggers
        - GPIO warnings are disabled to suppress pin 20 warnings
        - All LEDs are initialized to off state
    """
    if config.PLATFORM != "rpi":
        return

    # Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
    GPIO.setmode(GPIO.BCM)
    for k in config.PLAYER_MAP:
        GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(k, GPIO.FALLING, button_event, bouncetime=50)

    for k in config.GPIO_LED_MAP:
        GPIO.setup(k, GPIO.OUT)

    # I have no idea where these warnings are coming from on pin 20, let's
    # disable them. maybe it's complaining because pin 20 is MOSI/SPI but we're
    # not using that and everything works fine.
    GPIO.setwarnings(False)

    set_all_leds(context)
