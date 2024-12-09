import queue
import cv2
import datetime
import threading
import os

from src.camera import CAMERA
from src.gpio import GPIO, PinMode

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "TASK"


class Task:
    _instances = {}

    def __call__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super(Task, cls).__call__()
        return cls._instances[cls]

    def __init__(self):
        # Configure pin
        self.PIN = 21
        GPIO.configure_pin(pin=self.PIN, mode=PinMode.INPUT, pullup=True, debouncing_time=50e-3)

        # counter
        self.index = 1
        self.save_queue = queue.Queue()
        self.display_queue = queue.Queue()

    @property
    def __is_sensor_high(self) -> bool:
        # inverse pullup logic
        return not GPIO.read_input(self.PIN)

    def __imsave_worker(self):
        dir = "images"

        # create directory
        if not os.path.exists(dir):
            CLI.printline(Level.INFO, "({:^10}) Create directory.".format(print_name))
            os.makedirs(dir)

        while True:
            try:
                image = self.save_queue.get()
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filepath = f"{dir}/{self.index}_{timestamp}.jpg"
                cv2.imwrite(filepath, image)
                CLI.printline(Level.INFO, "({:^10}) Image saved.".format(print_name))
            except Exception as e:
                CLI.printline(Level.ERROR, "({:^10}) {}".format(print_name, e))

    def start(self):
        image_queued = False

        # start worker threads
        threading.Thread(target=self.__imsave_worker, daemon=True).start()

        CLI.printline(Level.INFO, "({:^10}) Start".format(print_name))

        while True:
            image = CAMERA.frame

            if image is not None:
                # display
                cv2.imshow("feed", image)
                cv2.waitKey(1)

                if not self.__is_sensor_high:
                    # reset
                    image_queued = False
                else:
                    # queue to save
                    if not image_queued:
                        self.save_queue.put(image)
                        image_queued = True


TASK = Task()
