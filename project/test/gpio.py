import sys
import os
import time

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.gpio import GPIO, PinMode

if __name__ == "__main__":
    # setup
    GPIO.configure_pin(21, PinMode.INPUT, pullup=False)

    while True:
        print(GPIO.read_input(21))
        time.sleep(0.01)
