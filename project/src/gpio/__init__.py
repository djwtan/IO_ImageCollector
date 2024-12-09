import gpiod
import time
import enum
import time
from typing import Dict, List, Optional

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "GPIO"


class PinMode(enum.Enum):
    OUTPUT = gpiod.LINE_REQ_DIR_OUT
    INPUT = gpiod.LINE_REQ_DIR_IN


class Output:
    HIGH = 1
    LOW = 0


class Index:
    OBJECT = 0
    MODE = 1
    DEBOUNCE_GEN = 2


class CommGPIO:
    _instances = {}

    def __call__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super(CommGPIO, cls).__call__()
        return cls._instances[cls]

    def __init__(self):
        self.chip = gpiod.Chip("gpiochip4")
        self.pins: Dict[int, List[gpiod.Chip, PinMode]] = {}

    def __debouncing_generator(self, pin: int, debounce_time: float = 0):
        state_previous = False
        state_debounced = False
        last_toggled = time.time()

        while True:
            state_current = self.pins[pin][Index.OBJECT].get_value() == 1
            time_current = time.time()

            if state_current != state_previous:
                if (time_current - last_toggled) >= debounce_time:
                    state_previous = state_current
                    last_toggled = time_current
                    state_debounced = state_current

            time.sleep(1 / 144)  # 144Hz
            yield state_debounced

    def configure_pin(
        self,
        pin: int,
        mode: PinMode,
        pullup: bool = False,
        consumer: str = "NULL",
        debouncing_time: Optional[float] = None,
    ):
        # Initialize List
        self.pins[pin] = [self.chip.get_line(pin), mode, None]

        # Configure object
        self.pins[pin][Index.OBJECT].request(
            consumer=consumer,
            type=mode.value,
            flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP if pullup else gpiod.LINE_REQ_FLAG_BIAS_PULL_DOWN,
        )
        CLI.printline(
            Level.INFO,
            "({:^10}) Pin{}: {}, {}".format(print_name, pin, mode.name, "PULL UP" if pullup else "PULL DOWN"),
        )

        # Debouncing?
        if debouncing_time:
            if self.pins[pin][Index.MODE] == PinMode.INPUT:
                self.pins[pin][Index.DEBOUNCE_GEN] = self.__debouncing_generator(pin, debouncing_time)
                # Initialize generator
                next(self.pins[pin][Index.DEBOUNCE_GEN])
                CLI.printline(
                    Level.INFO, "({:^10}) Debouncing -> {}s at Pin{}".format(print_name, debouncing_time, pin)
                )
            else:
                CLI.printline(Level.WARNING, "({:^10}) Debouncing not available for output".format(print_name))

    def read_input(self, pin: int) -> bool:
        # current value without debounce
        if self.pins[pin][Index.DEBOUNCE_GEN] is None:
            return self.pins[pin][Index.OBJECT].get_value() == 1

        # debounced value from the generator
        return next(self.pins[pin][Index.DEBOUNCE_GEN])

    def write_output(self, pin: int, output: Output):
        self.pins[pin][Index.OBJECT].set_value(output)


GPIO = CommGPIO()
