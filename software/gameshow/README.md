# rpi Gameshow

This is a set of work that I started about 8 years ago that implements a four player gameshow buzzer system for "The Dirty Talk Game Show."

It consists of a carrier board that a rPi 4 can be mounted to, and a set of custom buzzers which can be cheaply manufactured from simple parts. 

It uses pygame to implement the game and GPIO pins on the rPi for lights and buzzers.

On a new checkout, you'll need to pull and rebuild the virtual environment. Do that like so:

## Installation

```
# set as needed
PYTHON=python3.9

rm -rf .venv
$PYTHON -m venv .venv
source .venv/bin/activate

# having this first will make things go easier
pip3 install --upgrade pip 
pip3 install wheel

# installs all dependencies
pip3 install -r requirements.txt
```
