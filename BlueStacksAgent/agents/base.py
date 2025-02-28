import abc
import os
from collections import deque
from typing import Tuple

from adbutils import adb, AdbDevice


class BaseAgent(abc.ABC):
    """
    Abstract Base Class for BlueStacks screen capture agents.
    This class defines common configuration and the interface for all capture methods.
    """

    def __init__(self,
                 adb_path: str = "adb",
                 adb_port: int = 5555,
                 resolution: Tuple[int, int] = None,
                 bitrate: int = 8000000,
                 max_fps: int = 30,
                 queue_size: int = 3):
        """
        :param resolution: Tuple (width, height) for the desired resolution, or None for native
        :param bitrate: Bitrate for video encoding (default 8Mbps)
        :param max_fps: Maximum frames per second (default 30)
        :param queue_size: Number of frames to buffer (default 3)
        """
        self.adb_path = adb_path
        self.adb_port = adb_port
        self.resolution = resolution
        self.bitrate = bitrate
        self.max_fps = max_fps
        self.queue_size = queue_size

        # Check if the resolution is valid
        if resolution is not None and not self._is_resolution_valid():
            raise ValueError(f"Invalid resolution: {self.resolution}")

        # Check if the bitrate is valid
        if not self._is_bitrate_valid():
            raise ValueError(f"Invalid bitrate: {self.bitrate}")

        # Check if the max_fps is valid
        if not self._is_max_fps_valid():
            raise ValueError(f"Invalid max_fps: {self.max_fps}")

        # Check if the queue_size is valid
        if not self._is_queue_size_valid():
            raise ValueError(f"Invalid queue_size: {self.queue_size}")

        # Create the frame buffer
        self.frame_buffer = deque(maxlen=self.queue_size)

        # Connect to ADB
        self._connect_adb()
        self.adb_device: AdbDevice = adb.device(serial=f"emulator-{self.adb_port}")

        self._is_streaming = False

    @abc.abstractmethod
    def _start_stream(self):
        """
        Start the screen capture stream internally, to be handled from the concrete instances.
        """

    def start_stream(self):
        """
        Start the screen capture stream.
        """
        self._start_stream()
        self._is_streaming = True

    @abc.abstractmethod
    def _stop_stream(self):
        """
        Stop the screen capture stream internally, to be handled from the concrete instances.
        """

    def stop_stream(self):
        """
        Stop the screen capture stream.
        """
        self._is_streaming = False
        self._stop_stream()

    def is_streaming(self):
        """
        Return whether the agent is currently streaming.
        """
        return self._is_streaming

    def _is_resolution_valid(self):
        """
        Check if the resolution is valid.
        """
        # Check if the resolution is a tuple of two integers
        return isinstance(self.resolution, tuple) and len(self.resolution) == 2 and all(
            isinstance(x, int) for x in self.resolution)

    def _is_bitrate_valid(self):
        """
        Check if the bitrate is valid.
        """
        # Check if the bitrate is a positive integer
        return isinstance(self.bitrate, int) and self.bitrate > 0

    def _is_max_fps_valid(self):
        """
        Check if the max_fps is valid.
        """
        # Check if the max_fps is a positive integer
        return isinstance(self.max_fps, int) and self.max_fps > 0

    def _is_queue_size_valid(self):
        """
        Check if the queue_size is valid.
        """
        # Check if the queue_size is a positive integer
        return isinstance(self.queue_size, int) and self.queue_size > 0

    def _insert_in_frame_buffer(self, frame):
        """
        Insert a frame into the frame buffer.
        """
        self.frame_buffer.append(frame)

    def _connect_adb(self):
        """
        Connect to ADB.
        """
        # Check if ADB is installed
        if not self._is_adb_installed():
            raise FileNotFoundError("ADB not found. Please install ADB and add it to the system PATH.")

    def _is_adb_installed(self):
        """
        Check if ADB is installed.
        """
        return os.system(f"{self.adb_path} --version") == 0
