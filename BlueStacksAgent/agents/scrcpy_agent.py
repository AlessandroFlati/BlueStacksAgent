import threading
import time
from .base import BaseAgent
# noinspection PyPackageRequirements
from scrcpy import Client

class ScrcpyAgent(BaseAgent):
    """
    Concrete implementation of BaseAgent using scrcpy.
    """

    def __init__(self,
                 adb_path: str = "adb",
                 adb_port: int = 5555,
                 resolution: tuple[int, int] = None,
                 bitrate: int = 8000000,
                 max_fps: int = 30,
                 queue_size: int = 3):
        super().__init__(adb_path, adb_port, resolution, bitrate, max_fps, queue_size)
        self.client = None
        self.thread = None

    def _stream_loop(self):
        # Instantiate the scrcpy client with desired parameters.
        # TODO: (Additional scrcpy options can be added as needed.)
        self.client = Client(device=self.adb_device, bitrate=self.bitrate, max_fps=self.max_fps)
        self.client.add_listener("frame", self._insert_in_frame_buffer)
        self.client.start(threaded=True)
        # Continue streaming until signaled to stop.
        while self._is_streaming:
            time.sleep(0.1)
        self.client.stop()

    def _start_stream(self):
        """
        Start the scrcpy stream.
        """
        self.thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.thread.start()

    def _stop_stream(self):
        """
        Stop the scrcpy stream.
        """
        if self.thread:
            self.thread.join()
