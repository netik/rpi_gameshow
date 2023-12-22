
arduino-cli compile --fqbn arduino:avr:nano gpio_to_serial/gpio_to_serial.ino 
arduino-cli upload -p /dev/cu.usbserial-84440 --fqbn arduino:avr:nano gpio_to_serial/gpio_to_serial.ino 
