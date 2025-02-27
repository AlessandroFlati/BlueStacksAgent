import abc

class BaseAgent(abc.ABC):
    """
    Abstract Base Class for BlueStacks screen capture agents.
    This class defines common configuration and the interface for all capture methods.
    """

    def __init__(self, adb_path="adb", resolution=None, bitrate=8000000, max_fps=30):
        """
        :param adb_path: Path to the adb executable (default assumes it's in PATH)
        :param resolution: Tuple (width, height) for the desired resolution, or None for native
        :param bitrate: Bitrate for video encoding (default 8Mbps)
        :param max_fps: Maximum frames per second (default 30)
        """
        self.adb_path = adb_path
        self.resolution = resolution
        self.bitrate = bitrate
        self.max_fps = max_fps
        self._is_streaming = False

    @abc.abstractmethod
    def start_stream(self, callback):
        """
        Start the screen capture stream and register a callback function.
        :param callback: a function that will be called on each captured frame.
        """

    @abc.abstractmethod
    def stop_stream(self):
        """
        Stop the screen capture stream.
        """

    def is_streaming(self):
        """
        Return whether the agent is currently streaming.
        """
        return self._is_streaming
