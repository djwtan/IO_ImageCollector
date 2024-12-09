import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.gpio import GPIO, PinMode

if __name__ == "__main__":
    # setup
    GPIO.configure_pin(21, PinMode.INPUT, pullup=True, debouncing_time=0.001)

    while True:
        print(GPIO.read_input(21))
