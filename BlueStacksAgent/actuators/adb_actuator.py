import abc

import numpy as np
from adbutils import AdbDevice

from .base import BaseActuator


class AdbActuator(BaseActuator, abc.ABC):
    def __init__(self, adb_device: AdbDevice):
        super().__init__()
        self.adb_device: AdbDevice = adb_device

    def tap(self, x, y):
        self.adb_device.shell(f"input tap {x} {y}")

    def swipe(self, x1, y1, x2, y2, duration):
        self.adb_device.shell(f"input swipe {x1} {y1} {x2} {y2} {duration}")

    def keyevent(self, key):
        self.adb_device.shell(f"input keyevent {key}")

    def text(self, text):
        self.adb_device.shell(f"input text {text}")

    def press(self, key):
        self.adb_device.shell(f"input press {key}")

    def longpress(self, key):
        self.adb_device.shell(f"input longpress {key}")


class AntiDetectionModifier:
    """
    This class is used to modify the behavior of the AdbActuator to avoid detection.
    """

    @staticmethod
    def randomize(x, y, width, height, margin=0.05) -> (int, int):
        """
        Changes the coordinates to avoid detection, making a normal distribution around the center of the tap area
        In order to avoid overflow, the coordinates are clipped to the allowed area minus a small margin
        :param x: center x-coordinate of the tap
        :param y: center y-coordinate of the tap
        :param width: width of the allowed area to tap
        :param height: height of the allowed area to tap
        :return: the modified coordinates
        """

        x = max(int(np.random.normal(x, width * (1 - margin) // 4)), x - width * (1 - margin) // 2)
        x = min(x, x + width * (1 - margin) // 2)

        y = max(int(np.random.normal(y, height * (1 - margin) // 4)), y - height * (1 - margin) // 2)
        y = min(y, y + height * (1 - margin) // 2)

        return x, y

    @staticmethod
    def tap(x, y, width, height) -> (int, int):
        """
        Modify the tap coordinates to avoid detection.
        :param x: center x-coordinate of the tap
        :param y: center y-coordinate of the tap
        :param width: width of the allowed area to tap
        :param height: height of the allowed area to tap
        :return: the modified coordinates
        """

        return AntiDetectionModifier.randomize(x, y, width, height)

    @staticmethod
    def swipe(x1, y1, x2, y2, width1, height1, width2, height2) -> (int, int, int, int):
        """
        Modify the swipe coordinates to avoid detection.
        :param x1: start x-coordinate of the swipe
        :param y1: start y-coordinate of the swipe
        :param x2: end x-coordinate of the swipe
        :param y2: end y-coordinate of the swipe
        :param width1: width of the allowed area to start the swipe
        :param height1: height of the allowed area to start the swipe
        :param width2: width of the allowed area to end the swipe
        :param height2: height of the allowed area to end the swipe
        :return: the modified coordinates
        """

        x1, y1 = AntiDetectionModifier.randomize(x1, y1, width1, height1)
        x2, y2 = AntiDetectionModifier.randomize(x2, y2, width2, height2)

        return x1, y1, x2, y2

    @staticmethod
    def keyevent(key) -> int:
        """
        Modify the keyevent to avoid detection.
        :param key: the key to press
        :return: the modified key
        """

        return key

    @staticmethod
    def text(text) -> str:
        """
        Modify the text to avoid detection.
        :param text: the text to input
        :return: the modified text
        """

        return text

    @staticmethod
    def press(key) -> int:
        """
        Modify the press to avoid detection.
        :param key: the key to press
        :return: the modified key
        """

        return key

    @staticmethod
    def longpress(key) -> int:
        """
        Modify the longpress to avoid detection.
        :param key: the key to press
        :return: the modified key
        """

        return key


class AntiDetectionAdbActuator(BaseActuator, abc.ABC):
    def __init__(self, adb_device: AdbDevice):
        super().__init__()
        self.adb_actuator = AdbActuator(adb_device)

    def tap(self, x, y, width, height):
        x, y = AntiDetectionModifier.tap(x, y, width, height)
        self.adb_actuator.tap(x, y)

    def swipe(self, x1, y1, x2, y2, width1, height1, width2, height2, duration):
        x1, y1, x2, y2 = AntiDetectionModifier.swipe(x1, y1, x2, y2, width1, height1, width2, height2)
        self.adb_actuator.swipe(x1, y1, x2, y2, duration)

    def keyevent(self, key):
        key = AntiDetectionModifier.keyevent(key)
        self.adb_actuator.keyevent(key)

    def text(self, text):
        text = AntiDetectionModifier.text(text)
        self.adb_actuator.text(text)

    def press(self, key):
        key = AntiDetectionModifier.press(key)
        self.adb_actuator.press(key)

    def longpress(self, key):
        key = AntiDetectionModifier.longpress(key)
        self.adb_actuator.longpress(key)
