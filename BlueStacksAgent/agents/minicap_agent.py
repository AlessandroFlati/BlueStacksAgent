from .base import BaseAgent


class MinicapAgent(BaseAgent):
    """
    Concrete implementation of BaseAgent using minicap.
    """

    def __init__(self, adb_path="adb", resolution=None, bitrate=8000000, max_fps=30):
        super().__init__(adb_path, resolution, bitrate, max_fps)
        raise NotImplementedError("MinicapAgent is not yet implemented.")

    def start_stream(self, callback):
        """
        Start the minicap stream and assign a callback to process each frame.
        :param callback: Function receiving the frame (e.g. a NumPy array).
        """
        raise NotImplementedError("MinicapAgent is not yet implemented.")

    def stop_stream(self):
        """
        Stop the minicap stream.
        """
        raise NotImplementedError("MinicapAgent is not yet implemented.")