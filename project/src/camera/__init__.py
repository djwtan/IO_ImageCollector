import cv2
import threading
import time
import subprocess

# ------------------------------------------------------------------------------------ #
from src import CLI
from src.CLI import Level

print_name = "CAMERA"


def get_camera_id():
    try:
        cmd = "v4l2-ctl --list-devices"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            lines = result.stdout.split("\n")
            ctn = 0
            for line in lines:
                ctn += 1
                if "USB" in line:  # Raspberry PI Camera
                    infos = lines[ctn].strip().split("/")  # Expect "/dev/video*"
                    for info in infos:
                        if "video" in info:
                            CLI.printline(Level.INFO, f"(get_camera_id)-Camera ID detected: {info}")
                            return (int)(info.replace("video", ""))
        else:
            CLI.printline(Level.ERROR, f"(get_camera_id) - {result.stderr}")
    except Exception as e:
        CLI.printline(Level.ERROR, f"(get_camera_id) - {e}")
    return None


class Camera:
    RETRY_DELAY = 1

    def __init__(self) -> None:
        self.__src = None
        self.__stream = None
        self.__frame = None

        self.__init_camera()

        camera_thread = threading.Thread(target=self.__update, daemon=True)
        camera_thread.start()

    def __init_camera(self) -> None:
        self.__src = get_camera_id()
        self.__stream = cv2.VideoCapture(self.__src)

    def __refresh(self) -> None:
        time.sleep(Camera.RETRY_DELAY)
        self.__init_camera()

    def __update(self) -> None:
        CLI.printline(Level.INFO, "({:^10}) Start Stream -> {}".format(print_name, self.__src))
        while True:
            try:
                (_, self.__frame) = self.__stream.read()

            except Exception as e:
                CLI.printline(Level.ERROR, "({:^10})-({:^8}) Exception -> {}".format(print_name, "UPDATE", e))
                self.__refresh()

    @property
    def frame(self):
        return self.__frame


# Create object
CAMERA = Camera()
