from .base import BaseAgent


class MinicapAgent(BaseAgent):
    """
    Concrete implementation of BaseAgent using minicap.
    """

    def __init__(self,
                 adb_path: str = "adb",
                 resolution: tuple[int, int] = None,
                 bitrate: int = 8000000,
                 max_fps: int = 30,
                 queue_size: int = 3):
        super().__init__(adb_path, resolution, bitrate, max_fps, queue_size)
        raise NotImplementedError("MinicapAgent is not yet implemented.")

    def _start_stream(self):
        """
        Start the minicap stream.
        """
        raise NotImplementedError("MinicapAgent is not yet implemented.")

    def _stop_stream(self):
        """
        Stop the minicap stream.
        """
        raise NotImplementedError("MinicapAgent is not yet implemented.")
