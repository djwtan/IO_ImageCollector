import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
from src.camera import CAMERA

if __name__ == "__main__":
    while True:
        try:
            frame = CAMERA.frame
            if frame is not None:
                cv2.imshow("frame", frame)
                cv2.waitKey(1)

        except KeyboardInterrupt:
            break
