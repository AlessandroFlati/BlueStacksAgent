import threading
import time
from .base import BaseAgent
from scrcpy import Client

class ScrcpyAgent(BaseAgent):
    """
    Concrete implementation of BaseAgent using scrcpy.
    """

    def __init__(self, adb_path="adb", resolution=None, bitrate=8000000, max_fps=30):
        super().__init__(adb_path, resolution, bitrate, max_fps)
        self.client = None
        self.callback = None
        self.thread = None

    def _stream_loop(self):
        # Instantiate the scrcpy client with desired parameters.
        # TODO: (Additional scrcpy options can be added as needed.)
        self.client = Client(bitrate=self.bitrate, max_fps=self.max_fps)
        self.client.add_listener("frame", self.callback)
        self.client.start(threaded=True)
        # Continue streaming until signaled to stop.
        while self._is_streaming:
            time.sleep(0.1)
        self.client.stop()

    def start_stream(self, callback):
        """
        Start the scrcpy stream and assign a callback to process each frame.
        :param callback: Function receiving the frame (e.g. a NumPy array).
        """
        self.callback = callback
        self._is_streaming = True
        self.thread = threading.Thread(target=self._stream_loop, daemon=True)
        self.thread.start()

    def stop_stream(self):
        """
        Stop the scrcpy stream.
        """
        self._is_streaming = False
        if self.thread:
            self.thread.join()
